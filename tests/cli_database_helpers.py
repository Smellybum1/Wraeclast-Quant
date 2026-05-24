from __future__ import annotations

import sqlite3
from pathlib import Path


def write_unrelated_sqlite_database(tmp_path: Path, name: str = "not_wq.db") -> Path:
    database_path = tmp_path / name
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    return database_path


def sqlite_table_names(database_path: Path) -> set[str]:
    with sqlite3.connect(database_path) as connection:
        return {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }


__all__ = ["sqlite_table_names", "write_unrelated_sqlite_database"]
