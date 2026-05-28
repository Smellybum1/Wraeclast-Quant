from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import calibration_args as _calibration_args
from cli_outcome_database_helpers import (
    calibration_reviewed_database as _calibration_reviewed_database,
)


runner = CliRunner()


def test_calibration_command_prints_local_summaries(tmp_path: Path) -> None:
    database_path = _calibration_reviewed_database(tmp_path)

    result = runner.invoke(app, _calibration_args(database_path))

    assert result.exit_code == 0
    assert "Calibration By Action" in result.output
    assert "Calibration By Score Bucket" in result.output
    assert "Average Score By Outcome" in result.output
    assert "Calibration Review Prompts" in result.output
    assert "WATCH has 1 negative outcome(s)" in result.output
    assert "Recent Reviewed Recommendations" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "local-only and read-only" in result.output
    assert "wq calibration-report --output-path data/processed/calibration_report.md" in result.output


def test_calibration_command_missing_database_is_non_mutating(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, _calibration_args(database_path))

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue.md" in result.output
    assert "wq review-queue --run-id <id> --decisions-output-path data/processed/outcome_decisions.json" in result.output
    assert "wq record-outcomes --input-path" in result.output
    assert "data/processed/outcome_decisions.json" in result.output
    assert "--dry-run" in result.output
    assert "positive=useful signal" in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()
