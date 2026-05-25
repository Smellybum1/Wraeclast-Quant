from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import daily_args as _daily_args
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_daily_requires_sample_data_or_input_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _daily_args(database_path=tmp_path / "snapshots.db"),
    )

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for daily runs." in result.output


def test_daily_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            input_path=input_path,
            database_path=tmp_path / "snapshots.db",
        ),
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output
