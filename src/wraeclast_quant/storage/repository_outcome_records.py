from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import RecommendationOutcomeRecord
from wraeclast_quant.storage.repository_outcome_policy import ALLOWED_OUTCOMES
from wraeclast_quant.storage.repository_support import (
    read_connection,
    recommendation_outcome_from_row,
    utc_now,
)


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
