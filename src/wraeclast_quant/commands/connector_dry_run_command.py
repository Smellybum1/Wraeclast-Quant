from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.collectors.source_connector import source_connector_from_review
from wraeclast_quant.commands._connector_support import load_fixture_resources
from wraeclast_quant.commands.connector_dry_run_rendering import print_connector_dry_run
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review


def register(app: typer.Typer) -> None:
    @app.command("connector-dry-run")
    def connector_dry_run(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            connector = source_connector_from_review(
                review,
                load_fixture_resources(resources_path),
            )
            result = connector.collect_fixture(fixture_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_dry_run(result)
