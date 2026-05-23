from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("review-queue")
    def review_queue(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        run = repository.analysis_run(run_id) if run_id is not None else repository.latest_run()
        if run is None:
            if run_id is None:
                console.print("No snapshots found.")
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        opportunities = repository.unreviewed_opportunities_for_run(run.id, limit=limit)
        if not opportunities:
            console.print(f"No unreviewed recommendations found for run #{run.id}.")
            return

        table = Table(title=f"Recommendation Review Queue - Run #{run.id}")
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
        console.print(
            "Use wq record-outcome --run-id "
            f"{run.id} --item-name <name> --outcome positive|neutral|negative"
        )

    @app.command("review-coverage")
    def review_coverage(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
    ) -> None:
        repository = SnapshotRepository(database_path)
        run = repository.analysis_run(run_id) if run_id is not None else repository.latest_run()
        if run is None:
            if run_id is None:
                console.print("No snapshots found.")
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        coverage = repository.review_coverage_for_run(run.id)
        table = Table(title=f"Recommendation Review Coverage - Run #{run.id}")
        table.add_column("Total", justify="right")
        table.add_column("Reviewed", justify="right")
        table.add_column("Unreviewed", justify="right")
        table.add_column("Reviewed %", justify="right")
        table.add_row(
            str(coverage.total_recommendations),
            str(coverage.reviewed_recommendations),
            str(coverage.unreviewed_recommendations),
            f"{coverage.reviewed_percent:.1f}%",
        )
        console.print(table)
