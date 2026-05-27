from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console
from wraeclast_quant.reports.review_queue_worksheet import local_review_caveat
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.watchlist import top_watchlist
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.models import ReviewCoverageRecord
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
            opportunities = top_watchlist(rank_opportunities(SAMPLE_ITEMS), limit=limit)
            console.print("Watchlist - Sample Data")
            table = Table(title="Watchlist")
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
            if not opportunities:
                console.print(f"No scored opportunities found for run #{run.id}.")
                return
            coverage = repository.review_coverage_for_run(run.id)
            console.print(f"Watchlist - Run #{run.id} ({run.source_mode})")
            table = Table(title="Watchlist")
        table.add_column("Item")
        table.add_column("Score", justify="right")
        table.add_column("Action")
        for opportunity in opportunities:
            table.add_row(
                opportunity.item_name,
                f"{opportunity.opportunity_score:.2f}",
                opportunity.action,
            )
        console.print(table)
        if not sample_data:
            console.print(local_review_caveat(run.source_mode))
            console.print(_review_next_action(run.id, coverage))


def _review_next_action(run_id: int, coverage: ReviewCoverageRecord) -> str:
    reviewed = f"{coverage.reviewed_recommendations}/{coverage.total_recommendations} reviewed"
    if coverage.unreviewed_recommendations:
        return (
            f"Review coverage: {reviewed}; {coverage.unreviewed_recommendations} unreviewed. "
            f"Next: wq review-queue --run-id {run_id} "
            "--output-path data/processed/review_queue.md."
        )
    return f"Review coverage: {reviewed}; all recommendations for run #{run_id} have outcomes."
