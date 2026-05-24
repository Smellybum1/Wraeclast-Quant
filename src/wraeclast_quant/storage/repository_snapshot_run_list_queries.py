from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repository_support import (
    analysis_run_from_row,
    read_connection,
)


def list_recent_runs_query(database_path: Path, limit: int = 5) -> list[AnalysisRunRecord]:
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(
            """
            SELECT id, created_at, source_mode, item_count
            FROM analysis_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [analysis_run_from_row(row) for row in rows]


__all__ = ["list_recent_runs_query"]
