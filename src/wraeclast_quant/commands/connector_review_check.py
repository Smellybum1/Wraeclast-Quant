from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_check_rendering import print_connector_check
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-check")
    def connector_check(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        result = check_connector_review(review, load_resources(resources_path))
        print_connector_check(result)

        if result.ready:
            console.print("Connector review is ready for source-specific implementation planning.")
            return

        raise typer.Exit(code=1)
