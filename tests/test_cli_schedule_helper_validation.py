from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import schedule_helper_args as _schedule_helper_args
from cli_manual_import_file_helpers import (
    write_invalid_manual_import_json as _write_invalid_manual_import_json,
)
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_schedule_helper_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(sample_data=True, input_path=input_path),
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output


def test_schedule_helper_requires_sample_data_or_input_path() -> None:
    result = runner.invoke(app, _schedule_helper_args())

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for schedule helper." in result.output


def test_schedule_helper_rejects_invalid_time() -> None:
    result = runner.invoke(app, _schedule_helper_args(sample_data=True, time="25:99"))

    assert result.exit_code != 0
    assert "Use --time in HH:MM 24-hour format." in result.output


def test_schedule_helper_rejects_invalid_import_file(tmp_path: Path) -> None:
    input_path = _write_invalid_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(input_path=input_path),
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output
