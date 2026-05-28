from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_review_queue_rendering import (
    print_no_snapshots,
    print_no_unreviewed_recommendations,
    print_review_coverage,
    print_review_queue,
)
from wraeclast_quant.commands.maintenance_outcome_review_outputs import (
    write_review_queue_outputs,
)
from wraeclast_quant.commands.maintenance_outcome_review_selection import (
    selected_review_coverage,
    selected_unreviewed_opportunities,
)
from wraeclast_quant.reports.calibration import (
    build_calibration,
    calibration_review_prompts,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.models import ReviewCoverageRecord
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
        run, opportunities = selected_unreviewed_opportunities(
            repository,
            run_id,
            limit=limit,
        )
        if run is None:
            if run_id is None:
                print_no_snapshots()
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        if not opportunities:
            coverage = repository.review_coverage_for_run(run.id)
            print_no_unreviewed_recommendations(
                run.id,
                calibration_prompts=_calibration_prompts_for_completed_run(
                    repository,
                    coverage,
                ),
            )
            return

        print_review_queue(run.id, run.source_mode, opportunities)
        write_review_queue_outputs(
            output_path=output_path,
            decisions_output_path=decisions_output_path,
            context_path=context_path,
            run=run,
            opportunities=opportunities,
        )

    @app.command("review-coverage")
    def review_coverage(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
    ) -> None:
        repository = SnapshotRepository(database_path)
        run, coverage = selected_review_coverage(repository, run_id)
        if run is None or coverage is None:
            if run_id is None:
                print_no_snapshots()
                return
            raise typer.BadParameter(f"analysis run #{run_id} was not found")

        print_review_coverage(
            run.id,
            run.source_mode,
            coverage,
            calibration_prompts=_calibration_prompts_for_completed_run(
                repository,
                coverage,
            ),
        )


def _calibration_prompts_for_completed_run(
    repository: SnapshotRepository,
    coverage: ReviewCoverageRecord,
) -> list[str]:
    if coverage.unreviewed_recommendations:
        return []
    return calibration_review_prompts(build_calibration(repository))
