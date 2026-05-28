from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_manual_import_command_helpers import inspect_import_args as _inspect_import_args
from cli_manual_import_file_helpers import write_invalid_manual_import_json as _write_invalid_manual_import_json
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_inspect_import_prints_read_only_diagnostics(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst", "Ashen Rune Core")

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code == 0
    assert "Manual Import Diagnostics" in result.output
    assert "Items" in result.output
    assert "2" in result.output
    assert "Average score" in result.output
    assert "Signal Averages" in result.output
    assert "Top Imported Opportunities" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "read-only" in result.output
    assert f"Next: wq validate-import --input-path {input_path}" in result.output


def test_inspect_import_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()


def test_inspect_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    input_path = _write_invalid_manual_import_json(tmp_path)

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code != 0
    assert "demand_momentum" in result.output
