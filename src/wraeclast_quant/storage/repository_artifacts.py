from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import ReportArtifactRecord, RunProvenanceRecord
from wraeclast_quant.storage.repository_support import (
    read_connection,
    report_artifact_from_row,
    run_provenance_from_row,
    utc_now,
)


class ArtifactProvenanceMixin:
    def save_report_artifact(
        self,
        run_id: int,
        path: Path,
        created_at: str | None = None,
    ) -> ReportArtifactRecord:
        timestamp = created_at or utc_now()
        path_value = str(path)
        with connect(self.database_path) as connection:
            initialize_schema(connection)
            cursor = connection.execute(
                """
                INSERT INTO report_artifacts (run_id, path, created_at)
                VALUES (?, ?, ?)
                """,
                (run_id, path_value, timestamp),
            )
            connection.commit()
            return ReportArtifactRecord(
                id=int(cursor.lastrowid),
                run_id=run_id,
                path=path_value,
                created_at=timestamp,
            )

    def report_artifacts_for_run(self, run_id: int) -> list[ReportArtifactRecord]:
        with read_connection(self.database_path) as connection:
            if connection is None:
                return []
            rows = connection.execute(
                """
                SELECT id, run_id, path, created_at
                FROM report_artifacts
                WHERE run_id = ?
                ORDER BY id DESC
                """,
                (run_id,),
            ).fetchall()
        return [report_artifact_from_row(row) for row in rows]

    def save_run_provenance(
        self,
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
        with connect(self.database_path) as connection:
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

    def run_provenance(self, run_id: int) -> RunProvenanceRecord | None:
        with read_connection(self.database_path) as connection:
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

    def latest_run_provenance(self) -> RunProvenanceRecord | None:
        latest = self.latest_run()
        if latest is None:
            return None
        return self.run_provenance(latest.id)
