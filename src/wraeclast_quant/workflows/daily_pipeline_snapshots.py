from __future__ import annotations

from pathlib import Path

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison, compare_opportunities
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def create_analysis_snapshot(
    database_path: Path,
    opportunities: list[ScoredOpportunity],
    source_mode: str,
) -> tuple[SnapshotRepository, AnalysisRunRecord, SnapshotComparison | None]:
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode=source_mode, item_count=len(opportunities))
    previous = repository.previous_run_before(run.id)
    repository.save_scored_opportunities(run.id, opportunities)
    comparison = None
    if previous is not None:
        comparison = compare_opportunities(
            previous=repository.scored_opportunities_for_run(previous.id),
            latest=repository.scored_opportunities_for_run(run.id),
            previous_run_id=previous.id,
            latest_run_id=run.id,
        )
    return repository, run, comparison
