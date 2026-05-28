from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    CurrencyExchangeUiObservationExportResult,
)


def ui_observation_export_safety_text() -> str:
    return (
        "Exported manual-import-compatible JSON from local UI observations only. "
        "No OAuth, live HTTP, scraping, game-client automation, snapshots, or publishing were performed."
    )


def ui_observation_validate_next_action(output_path: object) -> str:
    return f"Next: wq validate-import --input-path {output_path}"


def ui_observation_review_sidecar_text(review_notes_path: object) -> str:
    return f"Review sidecar: {review_notes_path}"


def ui_observation_capture_flags_text(
    flag_count: int,
    review_notes_path: object | None,
) -> str:
    if flag_count <= 0:
        return "Capture review flags: none."
    if review_notes_path is None:
        return (
            f"Capture review flags: {flag_count}; rerun with "
            "--review-notes-output-path <file> to inspect them before wq daily."
        )
    return f"Capture review flags: {flag_count}; inspect {review_notes_path} before wq daily."


def ui_observation_daily_next_action(output_path: object) -> str:
    return f"Then: wq daily --input-path {output_path}"


def print_currency_exchange_ui_observation_export(
    result: CurrencyExchangeUiObservationExportResult,
) -> None:
    table = Table(title="Currency Exchange UI Observation Export")
    table.add_column("Source")
    table.add_column("Items", justify="right")
    table.add_column("Output Path", no_wrap=False)
    table.add_column("Review Notes", no_wrap=False)
    table.add_column("Capture Flags", justify="right")
    table.add_row(
        result.source_name,
        str(result.item_count),
        str(result.output_path),
        str(result.review_notes_path) if result.review_notes_path is not None else "not written",
        str(result.capture_review_flag_count),
    )
    console.print(table)
    console.print(ui_observation_export_safety_text())
    console.print(ui_observation_validate_next_action(result.output_path))
    if result.review_notes_path is not None:
        console.print(ui_observation_review_sidecar_text(result.review_notes_path))
    console.print(
        ui_observation_capture_flags_text(
            result.capture_review_flag_count,
            result.review_notes_path,
        )
    )
    console.print(ui_observation_daily_next_action(result.output_path))


__all__ = [
    "print_currency_exchange_ui_observation_export",
    "ui_observation_capture_flags_text",
    "ui_observation_daily_next_action",
    "ui_observation_export_safety_text",
    "ui_observation_review_sidecar_text",
    "ui_observation_validate_next_action",
]
