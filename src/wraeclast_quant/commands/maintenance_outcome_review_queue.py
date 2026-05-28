from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_review_queue_rendering import (
    print_no_snapshots,
    print_no_unreviewed_recommendations,
    print_review_coverage,
    print_review_queue,
)
from wraeclast_quant.commands.maintenance_outcome_review_context import (
    read_review_queue_context,
)
from wraeclast_quant.reports.review_queue_commands import record_outcomes_dry_run_command
from wraeclast_quant.reports.review_queue_decisions import (
    write_review_queue_decisions_template,
)
from wraeclast_quant.reports.review_queue_worksheet import write_review_queue_worksheet
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command("review-queue")
    def review_queue(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
        output_path: Path | None = typer.Option(
            None,
            "--output-path",
            help="Write a local Markdown review worksheet for the unreviewed queue.",
        ),
        decisions_output_path: Path | None = typer.Option(
            None,
            "--decisions-output-path",
            help="Write a local JSON outcome decisions template for record-outcomes.",
        ),
        context_path: Path | None = typer.Option(
            None,
            "--context-path",
            help="Optional local Markdown context file to embed in the review worksheet.",
        ),
    ) -> None:
        if context_path is not None and output_path is None:
            raise typer.BadParameter("Use --context-path together with --output-path.")
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

        print_review_queue(run.id, run.source_mode, opportunities)
        if output_path is not None:
            context_markdown = read_review_queue_context(context_path) if context_path is not None else None
            write_review_queue_worksheet(
                output_path,
                run_id=run.id,
                source_mode=run.source_mode,
                opportunities=opportunities,
                context_markdown=context_markdown,
            )
            typer.echo(f"Wrote review queue worksheet to {output_path}")
        if decisions_output_path is not None:
            write_review_queue_decisions_template(
                decisions_output_path,
                run_id=run.id,
                opportunities=opportunities,
            )
            typer.echo(f"Wrote outcome decisions template to {decisions_output_path}")
            typer.echo(
                f"Next: fill outcome labels, then run "
                f"{record_outcomes_dry_run_command(str(decisions_output_path))}."
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
                print_no_snapshots()
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        coverage = repository.review_coverage_for_run(run.id)
        print_review_coverage(run.id, run.source_mode, coverage)
