from wraeclast_quant.commands.connector_fixture_export_rendering import (
    connector_fixture_export_safety_text,
    connector_fixture_export_validation_next_action,
)


def test_connector_fixture_export_safety_text_preserves_cli_output() -> None:
    assert connector_fixture_export_safety_text() == (
        "Exported manual-import-compatible JSON. "
        "No network requests were made and no snapshots were created."
    )


def test_connector_fixture_export_validation_next_action_preserves_cli_output() -> None:
    assert connector_fixture_export_validation_next_action(
        "data/processed/manual_import.json"
    ) == (
        "Next: wq validate-import --input-path data/processed/manual_import.json"
    )
