from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repository_support import (
    analysis_run_from_row,
    read_connection,
    stored_opportunity_from_row,
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


def scored_opportunities_for_run_query(
    database_path: Path,
    run_id: int,
    limit: int | None = None,
) -> list[StoredOpportunityRecord]:
    query = """
        SELECT id, run_id, item_name, opportunity_score, action, inputs_json
        FROM scored_opportunities
        WHERE run_id = ?
        ORDER BY opportunity_score DESC, item_name ASC
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
