from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items
from wraeclast_quant.importers.summary import ManualImportSummary, summarize_opportunities
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def load_manual_opportunities(input_path: Path) -> list[ScoredOpportunity]:
    try:
        return rank_opportunities(load_manual_items(input_path))
    except ManualImportError as error:
        raise typer.BadParameter(str(error)) from error


def record_manual_import_run(
    database_path: Path,
    opportunities: list[ScoredOpportunity],
) -> AnalysisRunRecord:
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(
        source_mode="manual-import",
        item_count=len(opportunities),
    )
    repository.save_scored_opportunities(run.id, opportunities)
    return run


def summarize_manual_opportunities(
    opportunities: list[ScoredOpportunity],
) -> ManualImportSummary:
    return summarize_opportunities(opportunities)


__all__ = [
    "load_manual_opportunities",
    "record_manual_import_run",
    "summarize_manual_opportunities",
]
