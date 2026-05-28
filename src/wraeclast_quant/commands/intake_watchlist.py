from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.intake_rendering import console
from wraeclast_quant.commands.intake_watchlist_rendering import (
    print_watchlist_review_guidance,
    print_watchlist_table,
)
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.calibration import build_calibration, calibration_review_prompts
from wraeclast_quant.reports.watchlist import top_watchlist
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command()
    def watchlist(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1),
        limit: int = typer.Option(5, "--limit", min=1, max=50),
        sample_data: bool = typer.Option(False, "--sample-data"),
    ) -> None:
        if sample_data:
            ranked_sample_items = rank_opportunities(SAMPLE_ITEMS)
            opportunities = top_watchlist(ranked_sample_items, limit=limit)
            total_count = len(ranked_sample_items)
            title = "Watchlist - Sample Data"
        else:
            repository = SnapshotRepository(database_path)
            run = repository.analysis_run(run_id) if run_id is not None else repository.latest_run()
            if run is None:
                if run_id is None:
                    console.print("No snapshots found.")
                else:
                    console.print(f"Analysis run #{run_id} was not found.")
                return
            opportunities = repository.scored_opportunities_for_run(run.id, limit=limit)
            total_count = run.item_count
            if not opportunities:
                console.print(f"No scored opportunities found for run #{run.id}.")
                return
            coverage = repository.review_coverage_for_run(run.id)
            calibration_prompts = calibration_review_prompts(build_calibration(repository))
            title = f"Watchlist - Run #{run.id} ({run.source_mode})"
        print_watchlist_table(title=title, opportunities=opportunities, total_count=total_count)
        if not sample_data:
            print_watchlist_review_guidance(
                run_id=run.id,
                source_mode=run.source_mode,
                coverage=coverage,
                calibration_prompts=calibration_prompts if not coverage.unreviewed_recommendations else [],
            )
