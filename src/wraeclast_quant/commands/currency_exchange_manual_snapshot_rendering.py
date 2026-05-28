from __future__ import annotations

from pathlib import Path

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_fixture_models import ConnectorFixture


def manual_snapshot_input_text(input_path: object) -> str:
    return f"Input snapshot: {input_path}"


def manual_snapshot_history_text(history_path: object) -> str:
    return f"History snapshot: {history_path}"


def manual_snapshot_fixture_written_text(output_fixture_path: object) -> str:
    return f"Wrote connector fixture: {output_fixture_path}"


def manual_snapshot_rows_text(row_count: int) -> str:
    return f"Manual snapshot rows: {row_count}"


def manual_snapshot_safety_text() -> str:
    return "Manual snapshot validation is local-only. No network requests were made."


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
    console.print(manual_snapshot_input_text(input_path))
    if history_path is not None:
        console.print(manual_snapshot_history_text(history_path))
    if output_fixture_path is not None:
        console.print(manual_snapshot_fixture_written_text(output_fixture_path))
    console.print(manual_snapshot_rows_text(len(fixture.items)))
    console.print(manual_snapshot_safety_text())


__all__ = [
    "manual_snapshot_fixture_written_text",
    "manual_snapshot_history_text",
    "manual_snapshot_input_text",
    "manual_snapshot_rows_text",
    "manual_snapshot_safety_text",
    "print_currency_exchange_manual_snapshot",
]
