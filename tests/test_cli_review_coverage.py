from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import review_coverage_args as _review_coverage_args
from cli_outcome_database_helpers import (
    fully_reviewed_calibration_prompt_database as _fully_reviewed_calibration_prompt_database,
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)
from cli_outcome_database_helpers import (
    two_run_database_with_second_reviewed as _two_run_database_with_second_reviewed,
)


runner = CliRunner()


def test_review_coverage_command_prints_latest_run_coverage(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, _review_coverage_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Review Coverage" in result.output
    assert "#1" in result.output
    assert "50.0%" in result.output
    assert "positive=useful signal" in result.output
    assert "Batch review next steps:" in result.output
    assert "wq review-queue --run-id 1" in result.output
    assert "data/processed/review_queue.md" in result.output
    assert "--decisions-output-path data/processed/outcome_decisions_run_1.json" in result.output
    assert "wq record-outcomes --input-path data/processed/outcome_decisions_run_1.json" in result.output
    assert "--dry-run" in result.output


def test_review_coverage_command_uses_requested_run_id(tmp_path: Path) -> None:
    database_path, first, _second = _two_run_database_with_second_reviewed(tmp_path)

    result = runner.invoke(
        app,
        _review_coverage_args(database_path, run_id=first.id),
    )

    assert result.exit_code == 0
    assert "0.0%" in result.output
    assert "Batch review next steps:" in result.output
    assert f"wq review-queue --run-id {first.id}" in result.output
    assert "data/processed/review_queue.md" in result.output
    assert "--decisions-output-path data/processed/outcome_decisions_run_1.json" in result.output


def test_review_coverage_points_fully_reviewed_prompt_patterns_to_calibration(
    tmp_path: Path,
) -> None:
    database_path, run = _fully_reviewed_calibration_prompt_database(tmp_path)

    result = runner.invoke(
        app,
        _review_coverage_args(database_path, run_id=run.id),
    )

    assert result.exit_code == 0
    assert "100.0%" in result.output
    assert "Calibration prompts: 2 local read-only prompt(s)." in result.output
    assert "Next: wq calibration" in result.output
    assert "do not retune scoring or change recommendations" in result.output
    assert "Batch review next steps:" not in result.output


def test_review_coverage_command_handles_no_snapshots(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _review_coverage_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
