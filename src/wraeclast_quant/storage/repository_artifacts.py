from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import ReportArtifactRecord, RunProvenanceRecord
from wraeclast_quant.storage.repository_artifact_records import (
    insert_report_artifact,
    select_report_artifacts_for_run,
)
from wraeclast_quant.storage.repository_provenance_records import (
    select_run_provenance,
    upsert_run_provenance,
)


class ArtifactProvenanceMixin:
    def save_report_artifact(
        self,
        run_id: int,
        path: Path,
        created_at: str | None = None,
    ) -> ReportArtifactRecord:
        return insert_report_artifact(self.database_path, run_id, path, created_at)

    def report_artifacts_for_run(self, run_id: int) -> list[ReportArtifactRecord]:
        return select_report_artifacts_for_run(self.database_path, run_id)

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
        return upsert_run_provenance(
            self.database_path,
            run_id,
            source_kind,
            resource_name,
            connector_id,
            access_method,
            metadata,
            created_at,
        )

    def run_provenance(self, run_id: int) -> RunProvenanceRecord | None:
        return select_run_provenance(self.database_path, run_id)

    def latest_run_provenance(self) -> RunProvenanceRecord | None:
        latest = self.latest_run()
        if latest is None:
            return None
        return self.run_provenance(latest.id)
