from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_reports_rendering import (
    print_no_outcome_reviews,
    print_outcome_report_written,
    print_outcome_review,
)
from wraeclast_quant.reports.calibration import (
    build_calibration,
    calibration_review_prompts,
)
from wraeclast_quant.reports.outcome_review import (
    DEFAULT_OUTCOME_REVIEW_PATH,
    write_outcome_review,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command("outcome-review")
    def outcome_review(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        records = repository.list_outcome_reviews(limit=limit)
        if not records:
            print_no_outcome_reviews()
            return

        summary = repository.outcome_review_summary_by_action()
        print_outcome_review(
            records,
            summary,
            calibration_prompts=calibration_review_prompts(
                build_calibration(repository)
            ),
        )

    @app.command("outcome-report")
    def outcome_report(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        output_path: Path = typer.Option(DEFAULT_OUTCOME_REVIEW_PATH, "--output-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        reviews = repository.list_outcome_reviews(limit=limit)
        written_path = write_outcome_review(
            reviews=reviews,
            summary_by_action=repository.outcome_review_summary_by_action(),
            path=output_path,
        )
        print_outcome_report_written(written_path, has_reviews=bool(reviews))
