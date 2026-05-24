from __future__ import annotations

from wraeclast_quant.storage.repositories import SnapshotRepository
from wraeclast_quant.workflows.daily_pipeline_models import RunProvenanceInput


def save_run_provenance(
    repository: SnapshotRepository,
    run_id: int,
    provenance: RunProvenanceInput | None,
) -> None:
    if provenance is None:
        return
    repository.save_run_provenance(
        run_id=run_id,
        source_kind=provenance.source_kind,
        resource_name=provenance.resource_name,
        connector_id=provenance.connector_id,
        access_method=provenance.access_method,
        metadata=provenance.metadata,
    )
