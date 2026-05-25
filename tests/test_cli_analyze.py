from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_report_helpers import analyze_sample_args as _analyze_sample_args


runner = CliRunner()


def test_analyze_sample_data(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(app, _analyze_sample_args(database_path))

    assert result.exit_code == 0
    assert "Stormglass Catalyst" in result.output


def test_analyze_sample_data_records_snapshot(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _analyze_sample_args(database_path),
    )

    assert result.exit_code == 0
    assert database_path.exists()
    assert "Recorded analysis run" in result.output
