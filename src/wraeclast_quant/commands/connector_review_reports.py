from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_review_report_rendering import print_connector_review_report_summary
from wraeclast_quant.commands.connector_review_report_workflow import (
    write_connector_review_report_for_review,
)


def register(app: typer.Typer) -> None:
    @app.command("connector-review-report")
    def connector_review_report_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        output_path: Path = typer.Option(..., "--output-path", help="Local Markdown report output path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        written = write_connector_review_report_for_review(
            review_path=review_path,
            output_path=output_path,
            resources_path=resources_path,
        )

        print_connector_review_report_summary(written.report, written.written_path)
