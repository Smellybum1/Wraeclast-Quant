from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_review_queue_rendering import (
    print_no_snapshots,
    print_no_unreviewed_recommendations,
    print_review_coverage,
    print_review_queue,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


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
                print_no_snapshots()
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        opportunities = repository.unreviewed_opportunities_for_run(run.id, limit=limit)
        if not opportunities:
            print_no_unreviewed_recommendations(run.id)
            return

        print_review_queue(run.id, opportunities)

    @app.command("review-coverage")
    def review_coverage(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
    ) -> None:
        repository = SnapshotRepository(database_path)
        run = repository.analysis_run(run_id) if run_id is not None else repository.latest_run()
        if run is None:
            if run_id is None:
                print_no_snapshots()
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        coverage = repository.review_coverage_for_run(run.id)
        print_review_coverage(run.id, coverage)
