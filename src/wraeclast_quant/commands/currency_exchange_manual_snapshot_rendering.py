from __future__ import annotations

from pathlib import Path

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_fixture_models import ConnectorFixture


def print_currency_exchange_manual_snapshot(
    *,
    fixture: ConnectorFixture,
    input_path: Path,
    history_path: Path | None,
    output_fixture_path: Path | None,
) -> None:
    table = Table(title="Currency Exchange Manual Snapshot")
    for column in ["Source", "Name", "Category", "Confidence", "Signals", "Notes"]:
        table.add_column(column, no_wrap=column not in {"Notes"})

    for item in fixture.items:
        table.add_row(
            fixture.source_name,
            item.name,
            item.category,
            item.confidence,
            "yes" if item.signals is not None else "no",
            item.notes,
        )

    console.print(table)
    console.print(f"Input snapshot: {input_path}")
    if history_path is not None:
        console.print(f"History snapshot: {history_path}")
    if output_fixture_path is not None:
        console.print(f"Wrote connector fixture: {output_fixture_path}")
    console.print(f"Manual snapshot rows: {len(fixture.items)}")
    console.print("Manual snapshot validation is local-only. No network requests were made.")


__all__ = ["print_currency_exchange_manual_snapshot"]
