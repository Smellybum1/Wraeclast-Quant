from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import RunProvenanceRecord
from wraeclast_quant.storage.repository_support import (
    read_connection,
    run_provenance_from_row,
)


def select_run_provenance(
    database_path: Path,
    run_id: int,
) -> RunProvenanceRecord | None:
    with read_connection(database_path) as connection:
        if connection is None:
            return None
        row = connection.execute(
            """
            SELECT
                run_id,
                source_kind,
                resource_name,
                connector_id,
                access_method,
                metadata_json,
                created_at
            FROM run_provenance
            WHERE run_id = ?
            LIMIT 1
            """,
            (run_id,),
        ).fetchone()
    return run_provenance_from_row(row) if row is not None else None


__all__ = ["select_run_provenance"]
