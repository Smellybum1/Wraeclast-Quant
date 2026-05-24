from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def report(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = _sample_opportunities(sample_data)
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
        console.print(f"Wrote market brief to {output_path}")
        console.print(f"Recorded report artifact for analysis run #{run.id} to {database_path}")


def _sample_opportunities(sample_data: bool):
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)
