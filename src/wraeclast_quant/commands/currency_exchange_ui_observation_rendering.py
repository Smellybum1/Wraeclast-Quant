from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    CurrencyExchangeUiObservationExportResult,
)


def print_currency_exchange_ui_observation_export(
    result: CurrencyExchangeUiObservationExportResult,
) -> None:
    table = Table(title="Currency Exchange UI Observation Export")
    table.add_column("Source")
    table.add_column("Items", justify="right")
    table.add_column("Output Path", no_wrap=False)
    table.add_column("Review Notes", no_wrap=False)
    table.add_row(
        result.source_name,
        str(result.item_count),
        str(result.output_path),
        str(result.review_notes_path) if result.review_notes_path is not None else "not written",
    )
    console.print(table)
    console.print(
        "Exported manual-import-compatible JSON from local UI observations only. "
        "No OAuth, live HTTP, scraping, game-client automation, snapshots, or publishing were performed."
    )
    console.print(f"Next: wq validate-import --input-path {result.output_path}")
    if result.review_notes_path is not None:
        console.print(f"Review sidecar: {result.review_notes_path}")
    console.print(f"Then: wq daily --input-path {result.output_path}")


__all__ = ["print_currency_exchange_ui_observation_export"]
