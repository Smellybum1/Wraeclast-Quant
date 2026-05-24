from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repository_outcome_policy import ALLOWED_OUTCOMES
from wraeclast_quant.storage.repository_support import read_connection


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


__all__ = ["outcome_review_summary_by_action_query"]
