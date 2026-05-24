from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import load_fixture_resources
from wraeclast_quant.commands.connector_fixture_export_rendering import print_connector_fixture_export
from wraeclast_quant.config.connector_fixtures import export_connector_fixture_signals
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review


def register(app: typer.Typer) -> None:
    @app.command("connector-fixture-export")
    def connector_fixture_export(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        output_path: Path = typer.Option(..., "--output-path", help="Manual-import-compatible JSON output path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            export = export_connector_fixture_signals(
                review,
                load_fixture_resources(resources_path),
                fixture_path,
                output_path,
            )
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_fixture_export(export)
