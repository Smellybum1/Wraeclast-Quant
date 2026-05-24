from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_fixtures import ConnectorFixtureRunResult
from wraeclast_quant.config.connector_policy import ConnectorReview


def print_connector_fixture_blockers(review: ConnectorReview, result: ConnectorFixtureRunResult) -> None:
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


def print_connector_fixture_rows(result: ConnectorFixtureRunResult) -> None:
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
