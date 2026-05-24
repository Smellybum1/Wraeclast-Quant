from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison, compare_opportunities
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_snapshot_comparison(
    repository: SnapshotRepository,
    previous: AnalysisRunRecord | None,
    latest: AnalysisRunRecord,
) -> SnapshotComparison | None:
    if previous is None:
        return None
    return compare_opportunities(
        previous=repository.scored_opportunities_for_run(previous.id),
        latest=repository.scored_opportunities_for_run(latest.id),
        previous_run_id=previous.id,
        latest_run_id=latest.id,
    )


__all__ = ["build_snapshot_comparison"]
