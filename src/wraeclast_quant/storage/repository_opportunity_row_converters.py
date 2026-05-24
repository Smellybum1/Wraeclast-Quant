from __future__ import annotations

import json
import sqlite3

from wraeclast_quant.storage.models import StoredOpportunityRecord


def stored_opportunity_from_row(row: sqlite3.Row) -> StoredOpportunityRecord:
    inputs = json.loads(str(row["inputs_json"]))
    return StoredOpportunityRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        item_name=str(row["item_name"]),
        opportunity_score=float(row["opportunity_score"]),
        action=str(row["action"]),
        inputs={str(key): float(value) for key, value in inputs.items()},
    )


__all__ = ["stored_opportunity_from_row"]
