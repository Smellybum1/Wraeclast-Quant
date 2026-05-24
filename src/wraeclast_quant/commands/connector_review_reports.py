from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_review_report_rendering import print_connector_review_report_summary
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    connector_review_report,
    load_connector_review,
    write_connector_review_report,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-review-report")
    def connector_review_report_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        output_path: Path = typer.Option(..., "--output-path", help="Local Markdown report output path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            resources = load_resources(resources_path)
            report = connector_review_report(review, resources)
            written_path = write_connector_review_report(review, resources, output_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_review_report_summary(report, written_path)
