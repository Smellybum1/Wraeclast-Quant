from __future__ import annotations

import sqlite3
from pathlib import Path

from wraeclast_quant.storage.database_summary_queries import (
    missing_required_tables,
    read_database_content_summary,
    read_table_names,
)
from wraeclast_quant.storage.health_models import DatabaseHealthResult
from wraeclast_quant.storage.schema import REQUIRED_SQLITE_TABLES, SQLITE_SCHEMA_VERSION


def read_database_health(
    connection: sqlite3.Connection,
    database_path: Path,
) -> DatabaseHealthResult:
    integrity_message = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
    integrity_ok = integrity_message.lower() == "ok"
    missing_tables = missing_required_tables(read_table_names(connection))
    if missing_tables:
        return DatabaseHealthResult(
            database_path=database_path,
            schema_version=SQLITE_SCHEMA_VERSION,
            required_tables=sorted(REQUIRED_SQLITE_TABLES),
            size_bytes=database_path.stat().st_size,
            integrity_ok=integrity_ok,
            integrity_message=integrity_message,
            missing_tables=missing_tables,
            analysis_run_count=None,
            scored_opportunity_count=None,
            report_artifact_count=None,
            recommendation_outcome_count=None,
            latest_run_id=None,
            latest_run_created_at=None,
            latest_run_source_mode=None,
            latest_run_item_count=None,
        )

    summary = read_database_content_summary(connection)

    return DatabaseHealthResult(
        database_path=database_path,
        schema_version=SQLITE_SCHEMA_VERSION,
        required_tables=sorted(REQUIRED_SQLITE_TABLES),
        size_bytes=database_path.stat().st_size,
        integrity_ok=integrity_ok,
        integrity_message=integrity_message,
        missing_tables=[],
        analysis_run_count=summary.analysis_run_count,
        scored_opportunity_count=summary.scored_opportunity_count,
        report_artifact_count=summary.report_artifact_count,
        recommendation_outcome_count=summary.recommendation_outcome_count,
        latest_run_id=summary.latest_run.id if summary.latest_run is not None else None,
        latest_run_created_at=summary.latest_run.created_at
        if summary.latest_run is not None
        else None,
        latest_run_source_mode=summary.latest_run.source_mode
        if summary.latest_run is not None
        else None,
        latest_run_item_count=summary.latest_run.item_count
        if summary.latest_run is not None
        else None,
    )
