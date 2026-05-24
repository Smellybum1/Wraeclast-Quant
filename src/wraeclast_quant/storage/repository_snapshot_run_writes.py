from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repository_support import utc_now


def create_analysis_run_record(
    database_path: Path,
    source_mode: str,
    item_count: int,
    created_at: str | None = None,
) -> AnalysisRunRecord:
    timestamp = created_at or utc_now()
    with connect(database_path) as connection:
        initialize_schema(connection)
        cursor = connection.execute(
            """
            INSERT INTO analysis_runs (created_at, source_mode, item_count)
            VALUES (?, ?, ?)
            """,
            (timestamp, source_mode, item_count),
        )
        connection.commit()
        return AnalysisRunRecord(
            id=int(cursor.lastrowid),
            created_at=timestamp,
            source_mode=source_mode,
            item_count=item_count,
        )


__all__ = ["create_analysis_run_record"]
