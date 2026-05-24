from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_plan_rendering import print_connector_plan
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-plan")
    def connector_plan(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        result = build_fetch_plan(review, load_resources(resources_path))
        print_connector_plan(review, result)
        if result.plan is None:
            raise typer.Exit(code=1)
