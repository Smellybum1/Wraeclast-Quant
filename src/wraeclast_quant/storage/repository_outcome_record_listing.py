from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import RecommendationOutcomeRecord
from wraeclast_quant.storage.repository_support import (
    read_connection,
    recommendation_outcome_from_row,
)


def list_recent_outcome_records(
    database_path: Path,
    limit: int = 20,
) -> list[RecommendationOutcomeRecord]:
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(
            """
            SELECT id, run_id, item_name, outcome, notes, observed_at
            FROM recommendation_outcomes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [recommendation_outcome_from_row(row) for row in rows]


__all__ = ["list_recent_outcome_records"]
