from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import load_fixture_resources
from wraeclast_quant.commands.connector_fixture_run_rendering import (
    print_connector_fixture_blockers,
    print_connector_fixture_rows,
)
from wraeclast_quant.config.connector_fixtures import run_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review


def register(app: typer.Typer) -> None:
    @app.command("connector-fixture-run")
    def connector_fixture_run(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            resources = load_fixture_resources(resources_path)
            result = run_connector_fixture(review, resources, fixture_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        if not result.ready:
            print_connector_fixture_blockers(review, result)
            raise typer.Exit(code=1)

        print_connector_fixture_rows(result)
