from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


@dataclass(frozen=True)
class MarketBriefReportResult:
    run: AnalysisRunRecord
    output_path: Path


def sample_report_opportunities(sample_data: bool) -> list[ScoredOpportunity]:
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)


def write_sample_market_brief_report(
    database_path: Path,
    opportunities: list[ScoredOpportunity],
) -> MarketBriefReportResult:
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
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
    output_path = write_market_brief(opportunities, comparison=comparison)
    repository.save_report_artifact(run.id, output_path)
    return MarketBriefReportResult(run=run, output_path=output_path)


__all__ = [
    "MarketBriefReportResult",
    "sample_report_opportunities",
    "write_sample_market_brief_report",
]
