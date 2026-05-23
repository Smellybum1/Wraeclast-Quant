from __future__ import annotations

import sqlite3
from pathlib import Path

from wraeclast_quant.storage.backup_models import (
    DatabaseBackupError,
    DatabaseBackupVerification,
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
            tables = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            missing_tables = sorted(REQUIRED_SQLITE_TABLES - tables)
            if missing_tables:
                raise DatabaseBackupError(
                    "Backup is missing required tables: " + ", ".join(missing_tables)
                )

            latest_run = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

            return DatabaseBackupVerification(
                backup_path=backup_path,
                schema_version=SQLITE_SCHEMA_VERSION,
                required_tables=sorted(REQUIRED_SQLITE_TABLES),
                size_bytes=backup_path.stat().st_size,
                analysis_run_count=_count_rows(connection, "analysis_runs"),
                scored_opportunity_count=_count_rows(connection, "scored_opportunities"),
                report_artifact_count=_count_rows(connection, "report_artifacts"),
                recommendation_outcome_count=_count_rows(
                    connection,
                    "recommendation_outcomes",
                ),
                latest_run_id=int(latest_run["id"]) if latest_run is not None else None,
                latest_run_created_at=str(latest_run["created_at"])
                if latest_run is not None
                else None,
                latest_run_source_mode=str(latest_run["source_mode"])
                if latest_run is not None
                else None,
                latest_run_item_count=int(latest_run["item_count"])
                if latest_run is not None
                else None,
            )
    except sqlite3.Error as error:
        raise DatabaseBackupError(f"Could not verify SQLite backup: {error}") from error


def _count_rows(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
