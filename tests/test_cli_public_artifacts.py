import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_market_flow_database_helpers import buy_crossing_database as _buy_crossing_database
from cli_market_flow_database_helpers import small_mover_database as _small_mover_database
from cli_public_artifact_export_command_helpers import (
    export_args as _export_args,
)


runner = CliRunner()


def test_export_command_writes_public_intel(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Wrote public intel export" in result.output
    assert "Stormglass Catalyst" in output_path.read_text(encoding="utf-8")


def test_export_command_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path = _small_mover_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path, big_delta=20),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert payload["alerts"] == []


def test_export_command_handles_no_snapshots(tmp_path: Path) -> None:
    database_path = tmp_path / "empty.db"
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert not output_path.exists()
