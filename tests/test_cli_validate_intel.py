from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_market_flow_database_helpers import single_buy_database as _single_buy_database
from cli_public_artifact_export_command_helpers import (
    export_args as _export_args,
    validate_intel_args as _validate_intel_args,
)
from cli_public_artifact_file_helpers import (
    write_public_intel_with_raw_inputs as _write_public_intel_with_raw_inputs,
)


runner = CliRunner()


def test_validate_intel_command_accepts_exported_public_intel(tmp_path: Path) -> None:
    database_path = _single_buy_database(tmp_path)
    output_path = tmp_path / "public_intel.json"
    runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    result = runner.invoke(app, _validate_intel_args(output_path))

    assert result.exit_code == 0
    assert "Public Intel Contract Validation" in result.output
    assert "Schema version" in result.output
    assert "1.0" in result.output
    assert "matches the local derived-only contract" in result.output


def test_validate_intel_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = _write_public_intel_with_raw_inputs(tmp_path)

    result = runner.invoke(app, _validate_intel_args(intel_path))

    assert result.exit_code != 0
    assert "Public Intel Contract Validation" in result.output
    assert "Raw/private field is not allowed" in result.output
