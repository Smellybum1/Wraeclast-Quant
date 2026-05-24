from __future__ import annotations

from pathlib import Path

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity


def save_scored_run(
    repository: SnapshotRepository,
    opportunities: list[ScoredOpportunity],
    source_mode: str = "sample-data",
) -> AnalysisRunRecord:
    run = repository.create_analysis_run(
        source_mode=source_mode,
        item_count=len(opportunities),
    )
    repository.save_scored_opportunities(run.id, opportunities)
    return run


def snapshots_args(database_path: Path) -> list[str]:
    return ["snapshots", "--database-path", str(database_path)]


def save_single_opportunity_run(
    repository: SnapshotRepository,
    name: str,
    score: float,
    action: str,
    source_mode: str = "sample-data",
) -> AnalysisRunRecord:
    return save_scored_run(
        repository,
        [opportunity(name, score, action)],
        source_mode=source_mode,
    )
