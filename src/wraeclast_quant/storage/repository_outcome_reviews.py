from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import OutcomeReviewRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repository_outcome_policy import ALLOWED_OUTCOMES
from wraeclast_quant.storage.repository_support import (
    outcome_review_from_row,
    read_connection,
    stored_opportunity_from_row,
)


def unreviewed_opportunities_for_run_query(
    database_path: Path,
    run_id: int,
    limit: int | None = None,
) -> list[StoredOpportunityRecord]:
    query = """
        SELECT
            scored.id,
            scored.run_id,
            scored.item_name,
            scored.opportunity_score,
            scored.action,
            scored.inputs_json
        FROM scored_opportunities AS scored
        LEFT JOIN recommendation_outcomes AS outcomes
          ON outcomes.run_id = scored.run_id
         AND lower(outcomes.item_name) = lower(scored.item_name)
        WHERE scored.run_id = ? AND outcomes.id IS NULL
        ORDER BY scored.opportunity_score DESC, scored.item_name ASC
    """
    params: tuple[int, ...] | tuple[int, int]
    if limit is None:
        params = (run_id,)
    else:
        query = f"{query} LIMIT ?"
        params = (run_id, limit)
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(query, params).fetchall()
    return [stored_opportunity_from_row(row) for row in rows]


def list_outcome_review_records(
    database_path: Path,
    limit: int | None = 20,
) -> list[OutcomeReviewRecord]:
    query = """
        SELECT
            outcomes.id,
            outcomes.run_id,
            outcomes.item_name,
            outcomes.outcome,
            outcomes.notes,
            outcomes.observed_at,
            scored.opportunity_score,
            scored.action
        FROM recommendation_outcomes AS outcomes
        JOIN scored_opportunities AS scored
          ON scored.run_id = outcomes.run_id
         AND lower(scored.item_name) = lower(outcomes.item_name)
        ORDER BY outcomes.id DESC
    """
    params: tuple[int, ...] = ()
    if limit is not None:
        query = f"{query} LIMIT ?"
        params = (limit,)
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(query, params).fetchall()
    return [outcome_review_from_row(row) for row in rows]


def outcome_review_summary_by_action_query(
    database_path: Path,
) -> dict[str, dict[str, int]]:
    with read_connection(database_path) as connection:
        if connection is None:
            return {}
        rows = connection.execute(
            """
            SELECT scored.action, outcomes.outcome, COUNT(*) AS count
            FROM recommendation_outcomes AS outcomes
            JOIN scored_opportunities AS scored
              ON scored.run_id = outcomes.run_id
             AND lower(scored.item_name) = lower(outcomes.item_name)
            GROUP BY scored.action, outcomes.outcome
            ORDER BY scored.action ASC, outcomes.outcome ASC
            """
        ).fetchall()

    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        action = str(row["action"])
        if action not in summary:
            summary[action] = {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}
        summary[action][str(row["outcome"])] = int(row["count"])
    return summary
