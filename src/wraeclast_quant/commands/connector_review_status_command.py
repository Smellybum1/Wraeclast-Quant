from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_review_status_rendering import print_connector_review_status
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    connector_review_status,
    load_connector_review,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-review-status")
    def connector_review_status_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        status = connector_review_status(review, load_resources(resources_path))
        print_connector_review_status(status)

        if status.check_result.ready:
            console.print("Connector review is ready for connector-check and connector-plan.")
        else:
            console.print(
                "Connector review is not ready. Resolve blockers before running connector-check."
            )
