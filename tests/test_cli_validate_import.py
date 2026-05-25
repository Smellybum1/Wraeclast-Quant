from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_manual_import_command_helpers import validate_import_args as _validate_import_args
from cli_manual_import_file_helpers import write_invalid_manual_import_json as _write_invalid_manual_import_json
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_validate_import_prints_valid_count_and_table(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        _validate_import_args(input_path),
    )

    assert result.exit_code == 0
    assert "Manual Import Validation" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Valid manual import: 1 items." in result.output


def test_validate_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    input_path = _write_invalid_manual_import_json(tmp_path)

    result = runner.invoke(
        app,
        _validate_import_args(input_path),
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_validate_import_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        _validate_import_args(input_path),
    )

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()
