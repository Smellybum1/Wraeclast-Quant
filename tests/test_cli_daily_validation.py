from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import daily_args as _daily_args


runner = CliRunner()


def test_daily_requires_sample_data_or_input_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _daily_args(database_path=tmp_path / "snapshots.db"),
    )

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for daily runs." in result.output
