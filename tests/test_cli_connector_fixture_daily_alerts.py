from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)
from cli_connector_fixture_data_helpers import (
    connector_fixture_daily_tuned_setup as _connector_fixture_daily_tuned_setup,
)


runner = CliRunner()


def test_connector_fixture_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path, fixture_path = _connector_fixture_daily_tuned_setup(tmp_path)

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            fixture_path=fixture_path,
            database_path=database_path,
            big_delta=20,
        ),
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output
