from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.models import StoredOpportunityRecord


def review_queue_decisions_payload(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "decisions": [
            {
                "item_name": opportunity.item_name,
                "outcome": "",
                "notes": "",
            }
            for opportunity in opportunities
        ],
    }


def write_review_queue_decisions_template(
    path: Path,
    *,
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            review_queue_decisions_payload(run_id, opportunities),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


__all__ = [
    "review_queue_decisions_payload",
    "write_review_queue_decisions_template",
]
