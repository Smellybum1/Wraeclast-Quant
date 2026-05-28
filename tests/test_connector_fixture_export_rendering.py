from wraeclast_quant.commands.connector_fixture_export_rendering import (
    connector_fixture_export_safety_text,
)


def test_connector_fixture_export_safety_text_preserves_cli_output() -> None:
    assert connector_fixture_export_safety_text() == (
        "Exported manual-import-compatible JSON. "
        "No network requests were made and no snapshots were created."
    )
