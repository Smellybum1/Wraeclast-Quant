from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
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

        table = Table(title="Connector Review Report")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Resource", review.resource_name)
        table.add_row("Output path", str(written_path))
        table.add_row("Connector check", "ready" if report.check_result.ready else "not ready")
        table.add_row(
            "Approval suggestion",
            report.approval.approval_suggestion if report.approval.suggestion_available else "None",
        )
        table.add_row(
            "Blockers",
            "\n".join(report.check_result.blockers) if report.check_result.blockers else "None",
        )
        console.print(table)
        console.print(
            "Connector review report is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector."
        )
