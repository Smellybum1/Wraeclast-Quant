from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.storage.db import connect, initialize_schema


def save_scored_opportunity_records(
    database_path: Path,
    run_id: int,
    opportunities: list[ScoredOpportunity],
) -> None:
    rows = [
        (
            run_id,
            opportunity.item_name,
            opportunity.opportunity_score,
            opportunity.action,
            json.dumps(opportunity.inputs.model_dump(), sort_keys=True),
        )
        for opportunity in opportunities
    ]
    with connect(database_path) as connection:
        initialize_schema(connection)
        connection.executemany(
            """
            INSERT INTO scored_opportunities (
                run_id,
                item_name,
                opportunity_score,
                action,
                inputs_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()


__all__ = ["save_scored_opportunity_records"]
