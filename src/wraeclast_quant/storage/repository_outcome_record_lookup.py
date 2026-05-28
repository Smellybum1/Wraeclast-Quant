from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repository_support import read_connection


def recommendation_outcome_exists_query(
    database_path: Path,
    run_id: int,
    item_name: str,
) -> bool:
    with read_connection(database_path) as connection:
        if connection is None:
            return False
        row = connection.execute(
            """
            SELECT 1
            FROM recommendation_outcomes
            WHERE run_id = ? AND lower(item_name) = lower(?)
            LIMIT 1
            """,
            (run_id, item_name.strip()),
        ).fetchone()
    return row is not None


__all__ = ["recommendation_outcome_exists_query"]
