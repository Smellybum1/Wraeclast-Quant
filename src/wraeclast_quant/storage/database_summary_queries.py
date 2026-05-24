from __future__ import annotations

import sqlite3

from wraeclast_quant.storage.database_summary_models import (
    DatabaseContentSummary,
    LatestRunSummary,
)
from wraeclast_quant.storage.schema import REQUIRED_SQLITE_TABLES


def read_table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row["name"])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def missing_required_tables(tables: set[str]) -> list[str]:
    return sorted(REQUIRED_SQLITE_TABLES - tables)


def read_database_content_summary(
    connection: sqlite3.Connection,
) -> DatabaseContentSummary:
    return DatabaseContentSummary(
        analysis_run_count=_count_rows(connection, "analysis_runs"),
        scored_opportunity_count=_count_rows(connection, "scored_opportunities"),
        report_artifact_count=_count_rows(connection, "report_artifacts"),
        recommendation_outcome_count=_count_rows(
            connection,
            "recommendation_outcomes",
        ),
        latest_run=_read_latest_run(connection),
    )


def _read_latest_run(connection: sqlite3.Connection) -> LatestRunSummary | None:
    row = connection.execute(
        """
        SELECT id, created_at, source_mode, item_count
        FROM analysis_runs
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return None

    return LatestRunSummary(
        id=int(row["id"]),
        created_at=str(row["created_at"]),
        source_mode=str(row["source_mode"]),
        item_count=int(row["item_count"]),
    )


def _count_rows(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])


__all__ = [
    "DatabaseContentSummary",
    "LatestRunSummary",
    "missing_required_tables",
    "read_database_content_summary",
    "read_table_names",
]
