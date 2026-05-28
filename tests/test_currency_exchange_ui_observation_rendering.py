from pathlib import Path

from wraeclast_quant.commands.currency_exchange_ui_observation_rendering import (
    ui_observation_daily_next_action,
    ui_observation_export_safety_text,
    ui_observation_review_sidecar_text,
    ui_observation_validate_next_action,
)


def test_ui_observation_export_safety_text_preserves_local_only_boundary() -> None:
    assert ui_observation_export_safety_text() == (
        "Exported manual-import-compatible JSON from local UI observations only. "
        "No OAuth, live HTTP, scraping, game-client automation, snapshots, or publishing were performed."
    )


def test_ui_observation_next_actions_preserve_cli_text() -> None:
    output_path = Path("data/processed/standard_currency_exchange_manual_import.json")
    review_notes_path = Path("data/processed/standard_currency_exchange_ui_observation_review.md")

    assert ui_observation_validate_next_action(output_path) == (
        f"Next: wq validate-import --input-path {output_path}"
    )
    assert ui_observation_review_sidecar_text(review_notes_path) == (
        f"Review sidecar: {review_notes_path}"
    )
    assert ui_observation_daily_next_action(output_path) == (
        f"Then: wq daily --input-path {output_path}"
    )
