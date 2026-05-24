from __future__ import annotations

import sqlite3
from pathlib import Path

from wraeclast_quant.storage.database_summary_queries import (
    missing_required_tables,
    read_database_content_summary,
    read_table_names,
)
from wraeclast_quant.storage.health_result_builders import (
    healthy_database_result,
    missing_tables_health_result,
)
from wraeclast_quant.storage.health_models import DatabaseHealthResult


def read_database_health(
    connection: sqlite3.Connection,
    database_path: Path,
) -> DatabaseHealthResult:
    integrity_message = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
    integrity_ok = integrity_message.lower() == "ok"
    missing_tables = missing_required_tables(read_table_names(connection))
    if missing_tables:
        return missing_tables_health_result(
            database_path=database_path,
            integrity_ok=integrity_ok,
            integrity_message=integrity_message,
            missing_tables=missing_tables,
        )

    summary = read_database_content_summary(connection)

    return healthy_database_result(
        database_path=database_path,
        integrity_ok=integrity_ok,
        integrity_message=integrity_message,
        summary=summary,
    )
