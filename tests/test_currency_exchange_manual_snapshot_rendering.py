from pathlib import Path

from wraeclast_quant.commands.currency_exchange_manual_snapshot_rendering import (
    manual_snapshot_fixture_written_text,
    manual_snapshot_history_text,
    manual_snapshot_input_text,
    manual_snapshot_rows_text,
    manual_snapshot_safety_text,
)


def test_manual_snapshot_path_text_preserves_cli_output() -> None:
    input_path = Path("data/manual/current_snapshot.json")
    history_path = Path("data/manual/previous_snapshot.json")
    fixture_path = Path("data/processed/currency_exchange_fixture.json")

    assert manual_snapshot_input_text(input_path) == f"Input snapshot: {input_path}"
    assert manual_snapshot_history_text(history_path) == f"History snapshot: {history_path}"
    assert manual_snapshot_fixture_written_text(fixture_path) == (
        f"Wrote connector fixture: {fixture_path}"
    )


def test_manual_snapshot_summary_text_preserves_cli_output() -> None:
    assert manual_snapshot_rows_text(2) == "Manual snapshot rows: 2"
    assert manual_snapshot_safety_text() == (
        "Manual snapshot validation is local-only. No network requests were made."
    )
