from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import RecommendationOutcomeRecord
from wraeclast_quant.storage.repository_support import utc_now


def save_recommendation_outcome_record(
    database_path: Path,
    run_id: int,
    item_name: str,
    outcome: str,
    notes: str,
    observed_at: str | None,
) -> RecommendationOutcomeRecord:
    timestamp = observed_at or utc_now()
    with connect(database_path) as connection:
        initialize_schema(connection)
        cursor = connection.execute(
            """
            INSERT INTO recommendation_outcomes (
                run_id,
                item_name,
                outcome,
                notes,
                observed_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, item_name, outcome, notes, timestamp),
        )
        connection.commit()
        return RecommendationOutcomeRecord(
            id=int(cursor.lastrowid),
            run_id=run_id,
            item_name=item_name,
            outcome=outcome,
            notes=notes,
            observed_at=timestamp,
        )


__all__ = ["save_recommendation_outcome_record"]
