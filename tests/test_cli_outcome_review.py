from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import outcome_review_args as _outcome_review_args
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)


runner = CliRunner()


def test_outcome_review_command_prints_joined_review_and_summary(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        notes="Manual review.",
    )

    result = runner.invoke(app, _outcome_review_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Outcome Review" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "76.00" in result.output
    assert "BUY" in result.output
    assert "positive" in result.output
    assert "Outcome Review By Action" in result.output
    assert "wq calibration" in result.output
    assert "wq outcome-report --output-path data/processed/outcome_review.md" in result.output


def test_outcome_review_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _outcome_review_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue.md" in result.output
    assert "data/processed/review_queue.md" in result.output
    assert "positive=useful signal" in result.output
