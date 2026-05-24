from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import RunProvenanceRecord
from wraeclast_quant.storage.repository_support import utc_now


def upsert_run_provenance(
    database_path: Path,
    run_id: int,
    source_kind: str,
    resource_name: str,
    connector_id: str,
    access_method: str,
    metadata: dict[str, object],
    created_at: str | None = None,
) -> RunProvenanceRecord:
    timestamp = created_at or utc_now()
    metadata_json = json.dumps(metadata, sort_keys=True)
    with connect(database_path) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            INSERT OR REPLACE INTO run_provenance (
                run_id,
                source_kind,
                resource_name,
                connector_id,
                access_method,
                metadata_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                source_kind,
                resource_name,
                connector_id,
                access_method,
                metadata_json,
                timestamp,
            ),
        )
        connection.commit()
    return RunProvenanceRecord(
        run_id=run_id,
        source_kind=source_kind,
        resource_name=resource_name,
        connector_id=connector_id,
        access_method=access_method,
        metadata=metadata,
        created_at=timestamp,
    )


__all__ = ["upsert_run_provenance"]
