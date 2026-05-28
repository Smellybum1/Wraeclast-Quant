from __future__ import annotations

from wraeclast_quant.storage.models import (
    AnalysisRunRecord,
    ReviewCoverageRecord,
    StoredOpportunityRecord,
)
from wraeclast_quant.storage.repositories import SnapshotRepository


def selected_review_run(
    repository: SnapshotRepository,
    run_id: int | None,
) -> AnalysisRunRecord | None:
    return repository.analysis_run(run_id) if run_id is not None else repository.latest_run()


def selected_unreviewed_opportunities(
    repository: SnapshotRepository,
    run_id: int | None,
    *,
    limit: int,
) -> tuple[AnalysisRunRecord | None, list[StoredOpportunityRecord]]:
    run = selected_review_run(repository, run_id)
    if run is None:
        return None, []
    return run, repository.unreviewed_opportunities_for_run(run.id, limit=limit)


def selected_review_coverage(
    repository: SnapshotRepository,
    run_id: int | None,
) -> tuple[AnalysisRunRecord | None, ReviewCoverageRecord | None]:
    run = selected_review_run(repository, run_id)
    if run is None:
        return None, None
    return run, repository.review_coverage_for_run(run.id)


__all__ = [
    "selected_review_coverage",
    "selected_review_run",
    "selected_unreviewed_opportunities",
]
