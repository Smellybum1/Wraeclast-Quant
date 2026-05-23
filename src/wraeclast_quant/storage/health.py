from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.storage.schema import REQUIRED_SQLITE_TABLES, SQLITE_SCHEMA_VERSION


class DatabaseHealthError(ValueError):
    """Raised when a local SQLite database cannot be checked."""


@dataclass(frozen=True)
class DatabaseHealthResult:
    database_path: Path
    schema_version: str
    required_tables: list[str]
    size_bytes: int
    integrity_ok: bool
    integrity_message: str
    missing_tables: list[str]
    analysis_run_count: int | None
    scored_opportunity_count: int | None
    report_artifact_count: int | None
    recommendation_outcome_count: int | None
    latest_run_id: int | None
    latest_run_created_at: str | None
    latest_run_source_mode: str | None
    latest_run_item_count: int | None

    @property
    def schema_ok(self) -> bool:
        return not self.missing_tables

    @property
    def ok(self) -> bool:
        return self.integrity_ok and self.schema_ok


def check_database_health(database_path: Path) -> DatabaseHealthResult | None:
    if not database_path.exists():
        return None
    if not database_path.is_file():
        raise DatabaseHealthError(f"Database path is not a file: {database_path}")

    try:
        with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            integrity_message = str(
                connection.execute("PRAGMA integrity_check").fetchone()[0]
            )
            integrity_ok = integrity_message.lower() == "ok"
            tables = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            missing_tables = sorted(REQUIRED_SQLITE_TABLES - tables)
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

            latest_run = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

            return DatabaseHealthResult(
                database_path=database_path,
                schema_version=SQLITE_SCHEMA_VERSION,
                required_tables=sorted(REQUIRED_SQLITE_TABLES),
                size_bytes=database_path.stat().st_size,
                integrity_ok=integrity_ok,
                integrity_message=integrity_message,
                missing_tables=[],
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
        raise DatabaseHealthError(f"Could not check SQLite database: {error}") from error


def _count_rows(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
