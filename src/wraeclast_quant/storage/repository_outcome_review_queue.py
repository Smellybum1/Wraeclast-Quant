from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import StoredOpportunityRecord
from wraeclast_quant.storage.repository_support import read_connection, stored_opportunity_from_row


def unreviewed_opportunities_for_run_query(
    database_path: Path,
    run_id: int,
    limit: int | None = None,
) -> list[StoredOpportunityRecord]:
    query = """
        SELECT
            scored.id,
            scored.run_id,
            scored.item_name,
            scored.opportunity_score,
            scored.action,
            scored.inputs_json
        FROM scored_opportunities AS scored
        LEFT JOIN recommendation_outcomes AS outcomes
          ON outcomes.run_id = scored.run_id
         AND lower(outcomes.item_name) = lower(scored.item_name)
        WHERE scored.run_id = ? AND outcomes.id IS NULL
        ORDER BY scored.opportunity_score DESC, scored.item_name ASC
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


__all__ = ["unreviewed_opportunities_for_run_query"]
