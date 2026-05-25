from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import calibration_args as _calibration_args
from cli_outcome_command_helpers import calibration_report_args as _calibration_report_args
from cli_outcome_database_helpers import (
    calibration_reviewed_database as _calibration_reviewed_database,
)
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)


runner = CliRunner()


def test_calibration_command_prints_local_summaries(tmp_path: Path) -> None:
    database_path = _calibration_reviewed_database(tmp_path)

    result = runner.invoke(app, _calibration_args(database_path))

    assert result.exit_code == 0
    assert "Calibration By Action" in result.output
    assert "Calibration By Score Bucket" in result.output
    assert "Average Score By Outcome" in result.output
    assert "Recent Reviewed Recommendations" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "local-only and read-only" in result.output


def test_calibration_command_missing_database_is_non_mutating(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, _calibration_args(database_path))

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_calibration_report_command_writes_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "calibration_report.md"
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(
        app,
        _calibration_report_args(database_path, output_path),
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote calibration report" in result.output
    assert "# Wraeclast Quant Recommendation Calibration" in report
    assert "Stormglass Catalyst" in report
    assert "Outcome Counts By Action" in report
