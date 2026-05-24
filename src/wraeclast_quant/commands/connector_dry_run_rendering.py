from __future__ import annotations

from rich.table import Table

from wraeclast_quant.collectors.source_connector import ConnectorResult
from wraeclast_quant.commands._connector_support import console


def print_connector_dry_run(result: ConnectorResult) -> None:
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
