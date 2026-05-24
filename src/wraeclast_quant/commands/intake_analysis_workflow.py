from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def sample_analysis_opportunities(sample_data: bool) -> list[ScoredOpportunity]:
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)


def record_analysis_run(
    database_path: Path,
    opportunities: list[ScoredOpportunity],
) -> AnalysisRunRecord:
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    return run


__all__ = [
    "record_analysis_run",
    "sample_analysis_opportunities",
]
