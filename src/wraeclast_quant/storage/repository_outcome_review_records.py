from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repository_support import outcome_review_from_row, read_connection


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


__all__ = ["list_outcome_review_records"]
