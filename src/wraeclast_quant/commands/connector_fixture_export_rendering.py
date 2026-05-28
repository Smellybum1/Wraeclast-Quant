from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_fixtures import ConnectorFixtureExportResult


def connector_fixture_export_safety_text() -> str:
    return (
        "Exported manual-import-compatible JSON. "
        "No network requests were made and no snapshots were created."
    )


def print_connector_fixture_export(export: ConnectorFixtureExportResult) -> None:
    table = Table(title="Connector Fixture Export")
    table.add_column("Source")
    table.add_column("Items")
    table.add_column("Output Path", no_wrap=False)
    table.add_row(export.source_name, str(export.item_count), str(export.output_path))
    console.print(table)
    console.print(connector_fixture_export_safety_text())


__all__ = [
    "connector_fixture_export_safety_text",
    "print_connector_fixture_export",
]
