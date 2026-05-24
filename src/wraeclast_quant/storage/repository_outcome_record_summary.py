from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repository_outcome_policy import ALLOWED_OUTCOMES
from wraeclast_quant.storage.repository_support import read_connection


def outcome_count_summary(database_path: Path) -> dict[str, int]:
    summary = {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}
    with read_connection(database_path) as connection:
        if connection is None:
            return summary
        rows = connection.execute(
            """
            SELECT outcome, COUNT(*) AS count
            FROM recommendation_outcomes
            GROUP BY outcome
            """
        ).fetchall()
    for row in rows:
        summary[str(row["outcome"])] = int(row["count"])
    return summary


__all__ = ["outcome_count_summary"]
