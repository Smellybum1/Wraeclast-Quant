from __future__ import annotations

import json
import sqlite3

from wraeclast_quant.storage.models import RunProvenanceRecord


def run_provenance_from_row(row: sqlite3.Row) -> RunProvenanceRecord:
    return RunProvenanceRecord(
        run_id=int(row["run_id"]),
        source_kind=str(row["source_kind"]),
        resource_name=str(row["resource_name"]),
        connector_id=str(row["connector_id"]),
        access_method=str(row["access_method"]),
        metadata=json.loads(str(row["metadata_json"])),
        created_at=str(row["created_at"]),
    )


__all__ = ["run_provenance_from_row"]
