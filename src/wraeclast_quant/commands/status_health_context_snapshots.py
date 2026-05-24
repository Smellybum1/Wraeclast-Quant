from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.storage.health import DatabaseHealthResult
from wraeclast_quant.storage.models import AnalysisRunRecord, ReviewCoverageRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


@dataclass(frozen=True)
class SnapshotStatusContext:
    latest: AnalysisRunRecord | None
    latest_run_id: int | None
    coverage: ReviewCoverageRecord | None


def load_snapshot_status_context(
    database_path: Path,
    database_health: DatabaseHealthResult | None,
) -> SnapshotStatusContext:
    latest = None
    coverage = None
    if database_health is not None and database_health.ok:
        repository = SnapshotRepository(database_path)
        latest = repository.latest_run()
        if latest is not None:
            coverage = repository.review_coverage_for_run(latest.id)
    return SnapshotStatusContext(
        latest=latest,
        latest_run_id=latest.id if latest is not None else None,
        coverage=coverage,
    )


__all__ = ["SnapshotStatusContext", "load_snapshot_status_context"]
