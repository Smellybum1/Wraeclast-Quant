from __future__ import annotations

import sqlite3
from pathlib import Path

from wraeclast_quant.storage.health_checks import read_database_health
from wraeclast_quant.storage.health_models import DatabaseHealthError, DatabaseHealthResult


def check_database_health(database_path: Path) -> DatabaseHealthResult | None:
    if not database_path.exists():
        return None
    if not database_path.is_file():
        raise DatabaseHealthError(f"Database path is not a file: {database_path}")

    try:
        with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            return read_database_health(connection, database_path)
    except sqlite3.Error as error:
        raise DatabaseHealthError(f"Could not check SQLite database: {error}") from error


__all__ = [
    "DatabaseHealthError",
    "DatabaseHealthResult",
    "check_database_health",
]
