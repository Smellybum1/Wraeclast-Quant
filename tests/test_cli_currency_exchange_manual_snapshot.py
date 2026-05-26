import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_manual_import_command_helpers import validate_import_args as _validate_import_args


runner = CliRunner()


def test_currency_exchange_manual_snapshot_prints_rows() -> None:
    result = runner.invoke(
        app,
        [
            "currency-exchange-manual-snapshot",
            "--input-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
        ],
    )

    assert result.exit_code == 0
    assert "Currency Exchange Manual Snapshot" in result.output
    assert "Chaos Orb / Divine Orb" in result.output
    assert "Manual snapshot rows: 2" in result.output
    assert "No network requests were made" in result.output


def test_currency_exchange_manual_snapshot_writes_connector_fixture_with_history(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"

    result = runner.invoke(
        app,
        [
            "currency-exchange-manual-snapshot",
            "--input-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--history-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--output-fixture-path",
            str(output_path),
        ],
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Wrote connector fixture" in result.output
    assert payload["source_name"] == "Path of Exile Currency Exchange API Preview"
    assert payload["items"][0]["signals"]["demand_momentum"] == 50.0


def test_currency_exchange_manual_snapshot_output_feeds_fixture_runner(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"
    write_result = runner.invoke(
        app,
        [
            "currency-exchange-manual-snapshot",
            "--input-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--history-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--output-fixture-path",
            str(output_path),
        ],
    )

    run_result = runner.invoke(
        app,
        _connector_fixture_run_args(fixture_path=output_path),
    )

    assert write_result.exit_code == 0
    assert run_result.exit_code == 0
    assert "Connector Fixture Rows" in run_result.output
    assert "Chaos Orb / Divine Orb" in run_result.output


def test_currency_exchange_manual_snapshot_output_exports_to_manual_import(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "currency_exchange_fixture.json"
    import_path = tmp_path / "currency_exchange_manual_import.json"
    write_result = runner.invoke(
        app,
        [
            "currency-exchange-manual-snapshot",
            "--input-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--history-path",
            "examples/pathofexile_currency_exchange_manual_snapshot_template.json",
            "--output-fixture-path",
            str(fixture_path),
        ],
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


def test_currency_exchange_manual_snapshot_rejects_invalid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.json"
    input_path.write_text('{"markets": []}', encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "currency-exchange-manual-snapshot",
            "--input-path",
            str(input_path),
        ],
    )

    assert result.exit_code != 0
    assert "manual snapshot" in result.output
