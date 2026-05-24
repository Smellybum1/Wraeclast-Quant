from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.database_summary_models import DatabaseContentSummary
from wraeclast_quant.storage.health_models import DatabaseHealthResult
from wraeclast_quant.storage.schema import REQUIRED_SQLITE_TABLES, SQLITE_SCHEMA_VERSION


def missing_tables_health_result(
    *,
    database_path: Path,
    integrity_ok: bool,
    integrity_message: str,
    missing_tables: list[str],
) -> DatabaseHealthResult:
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


def healthy_database_result(
    *,
    database_path: Path,
    integrity_ok: bool,
    integrity_message: str,
    summary: DatabaseContentSummary,
) -> DatabaseHealthResult:
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


__all__ = ["healthy_database_result", "missing_tables_health_result"]
