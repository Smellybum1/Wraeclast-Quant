import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    MANUAL_SNAPSHOT_TEMPLATE as _MANUAL_SNAPSHOT_TEMPLATE,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    currency_exchange_manual_snapshot_args as _currency_exchange_manual_snapshot_args,
)
from cli_manual_import_command_helpers import validate_import_args as _validate_import_args


runner = CliRunner()


def test_currency_exchange_manual_snapshot_output_exports_to_manual_import(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "currency_exchange_fixture.json"
    import_path = tmp_path / "currency_exchange_manual_import.json"
    write_result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=fixture_path,
        ),
    )
    export_result = runner.invoke(
        app,
        _connector_fixture_export_args(
            fixture_path=fixture_path,
            output_path=import_path,
        ),
    )
    validate_result = runner.invoke(app, _validate_import_args(import_path))
    payload = json.loads(import_path.read_text(encoding="utf-8"))

    assert write_result.exit_code == 0
    assert export_result.exit_code == 0
    assert validate_result.exit_code == 0
    assert payload["items"][0]["name"] == "Chaos Orb / Divine Orb"
    assert "signals" in payload["items"][0]
