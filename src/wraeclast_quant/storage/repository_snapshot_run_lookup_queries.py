from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repository_support import (
    analysis_run_from_row,
    read_connection,
)


def latest_run_query(database_path: Path) -> AnalysisRunRecord | None:
    with read_connection(database_path) as connection:
        if connection is None:
            return None
        row = connection.execute(
            """
            SELECT id, created_at, source_mode, item_count
            FROM analysis_runs
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    return analysis_run_from_row(row) if row is not None else None


def previous_run_before_query(database_path: Path, run_id: int) -> AnalysisRunRecord | None:
    with read_connection(database_path) as connection:
        if connection is None:
            return None
        row = connection.execute(
            """
            SELECT id, created_at, source_mode, item_count
            FROM analysis_runs
            WHERE id < ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
    return analysis_run_from_row(row) if row is not None else None


def analysis_run_query(database_path: Path, run_id: int) -> AnalysisRunRecord | None:
    with read_connection(database_path) as connection:
        if connection is None:
            return None
        row = connection.execute(
            """
            SELECT id, created_at, source_mode, item_count
            FROM analysis_runs
            WHERE id = ?
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
    return analysis_run_from_row(row) if row is not None else None


__all__ = ["analysis_run_query", "latest_run_query", "previous_run_before_query"]
