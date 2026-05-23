from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console, load_fixture_resources
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

        table = Table(title="Connector Fixture Export")
        table.add_column("Source")
        table.add_column("Items")
        table.add_column("Output Path", no_wrap=False)
        table.add_row(export.source_name, str(export.item_count), str(export.output_path))
        console.print(table)
        console.print(
            "Exported manual-import-compatible JSON. No network requests were made and no snapshots were created."
        )
