from __future__ import annotations

import sqlite3
from pathlib import Path

from wraeclast_quant.storage.backup_models import (
    DatabaseBackupError,
    DatabaseBackupVerification,
)
from wraeclast_quant.storage.database_summary_queries import (
    missing_required_tables,
    read_database_content_summary,
    read_table_names,
)
from wraeclast_quant.storage.schema import REQUIRED_SQLITE_TABLES, SQLITE_SCHEMA_VERSION


def verify_database_backup(backup_path: Path) -> DatabaseBackupVerification:
    if not backup_path.exists():
        raise DatabaseBackupError(f"Backup file not found: {backup_path}")
    if not backup_path.is_file():
        raise DatabaseBackupError(f"Backup path is not a file: {backup_path}")

    try:
        with sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            missing_tables = missing_required_tables(read_table_names(connection))
            if missing_tables:
                raise DatabaseBackupError(
                    "Backup is missing required tables: " + ", ".join(missing_tables)
                )

            summary = read_database_content_summary(connection)

            return DatabaseBackupVerification(
                backup_path=backup_path,
                schema_version=SQLITE_SCHEMA_VERSION,
                required_tables=sorted(REQUIRED_SQLITE_TABLES),
                size_bytes=backup_path.stat().st_size,
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
    except sqlite3.Error as error:
        raise DatabaseBackupError(f"Could not verify SQLite backup: {error}") from error
