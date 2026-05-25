from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import daily_args as _daily_args
from cli_daily_fixture_helpers import small_mover_daily_setup as _small_mover_daily_setup


runner = CliRunner()


def test_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path, input_path = _small_mover_daily_setup(tmp_path)

    result = runner.invoke(
        app,
        _daily_args(input_path=input_path, database_path=database_path, big_delta=20),
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output
