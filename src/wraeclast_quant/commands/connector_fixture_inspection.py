from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.commands._connector_support import console, load_fixture_resources
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
            table = Table(title="Connector Fixture Run")
            table.add_column("Resource")
            table.add_column("Access")
            table.add_column("Ready")
            table.add_column("Blockers", no_wrap=False)
            table.add_row(
                review.resource_name,
                review.access_method,
                "no",
                "\n".join(result.blockers) if result.blockers else "Unknown fixture error.",
            )
            console.print(table)
            raise typer.Exit(code=1)

        assert result.fixture is not None
        assert result.fetch_plan is not None
        table = Table(title="Connector Fixture Rows")
        for column in ["Source", "Name", "Category", "Price", "Confidence", "Notes"]:
            table.add_column(column, no_wrap=column != "Notes")

        for item in result.rows:
            table.add_row(
                result.fixture.source_name,
                item.name,
                item.category,
                item.price_text,
                item.confidence,
                item.notes,
            )
        console.print(table)
        console.print(f"Fixture rows: {len(result.rows)}")
        console.print(f"Fetch plan cache path: {result.fetch_plan.cache_path}")
        console.print("Fixture run is local-only. No network requests were made and no files were written.")

    @app.command("connector-dry-run")
    def connector_dry_run(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            connector = FixtureSourceConnector.from_review(
                review,
                load_fixture_resources(resources_path),
            )
            result = connector.collect_fixture(fixture_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        table = Table(title="Connector Dry Run")
        for column in ["Connector", "Resource", "Name", "Category", "Price", "Confidence", "Notes"]:
            table.add_column(column, no_wrap=column != "Notes")

        for row in result.rows:
            table.add_row(
                result.connector_class,
                result.resource_name,
                row.name,
                row.category,
                row.price_text,
                row.confidence,
                row.notes,
            )
        console.print(table)
        console.print(f"Connector ID: {result.connector_id}")
        console.print(f"Future cache path: {result.fetch_plan.cache_path}")
        console.print("Connector dry-run is local-only. No network requests were made and no files were written.")
