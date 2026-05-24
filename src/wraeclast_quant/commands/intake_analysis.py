from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.intake_rendering import console, print_opportunities
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command()
    def analyze(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = _sample_opportunities(sample_data)
        print_opportunities("Scored Opportunities", opportunities)
        run = _record_analysis_run(database_path, opportunities)
        console.print(f"Recorded analysis run #{run.id} to {database_path}")


def _sample_opportunities(sample_data: bool):
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)


def _record_analysis_run(database_path: Path, opportunities):
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    return run
