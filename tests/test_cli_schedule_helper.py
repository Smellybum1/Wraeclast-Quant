from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import schedule_helper_args as _schedule_helper_args
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_schedule_helper_sample_data_prints_scheduler_guidance() -> None:
    result = runner.invoke(app, _schedule_helper_args(sample_data=True, time="09:30"))

    assert result.exit_code == 0
    assert "Daily command:" in result.output
    assert "wq daily --sample-data" in result.output
    assert "schtasks /Create" in result.output
    assert "/ST 09:30" in result.output
    assert "PowerShell one-liner alternative:" in result.output
    assert "does not create scheduled tasks" in result.output


def test_schedule_helper_input_path_validates_and_prints_daily_command(
    tmp_path: Path,
) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(input_path=input_path),
    )

    assert result.exit_code == 0
    assert "wq daily --input-path" in result.output
    assert str(input_path) in result.output
    assert "schtasks /Create" in result.output


def test_schedule_helper_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, _schedule_helper_args(sample_data=True))

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()
