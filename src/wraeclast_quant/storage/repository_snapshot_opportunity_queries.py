from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import StoredOpportunityRecord
from wraeclast_quant.storage.repository_support import (
    read_connection,
    stored_opportunity_from_row,
)


def scored_opportunities_for_run_query(
    database_path: Path,
    run_id: int,
    limit: int | None = None,
) -> list[StoredOpportunityRecord]:
    query = """
        SELECT id, run_id, item_name, opportunity_score, action, inputs_json
        FROM scored_opportunities
        WHERE run_id = ?
        ORDER BY opportunity_score DESC, item_name ASC
    """
    params: tuple[int, ...] | tuple[int, int]
    if limit is None:
        params = (run_id,)
    else:
        query = f"{query} LIMIT ?"
        params = (run_id, limit)
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(query, params).fetchall()
    return [stored_opportunity_from_row(row) for row in rows]


__all__ = ["scored_opportunities_for_run_query"]
