from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repository_support import read_connection


def item_exists_for_run_query(database_path: Path, run_id: int, item_name: str) -> bool:
    normalized = item_name.strip().casefold()
    with read_connection(database_path) as connection:
        if connection is None:
            return False
        row = connection.execute(
            """
            SELECT 1
            FROM scored_opportunities
            WHERE run_id = ? AND lower(item_name) = lower(?)
            LIMIT 1
            """,
            (run_id, normalized),
        ).fetchone()
    return row is not None


__all__ = ["item_exists_for_run_query"]
