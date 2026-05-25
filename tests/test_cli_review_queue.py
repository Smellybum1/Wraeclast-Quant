from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import review_coverage_args as _review_coverage_args
from cli_outcome_command_helpers import review_queue_args as _review_queue_args
from cli_outcome_database_helpers import (
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)
from cli_outcome_database_helpers import two_run_database as _two_run_database
from cli_outcome_database_helpers import (
    two_run_database_with_second_reviewed as _two_run_database_with_second_reviewed,
)


runner = CliRunner()


def test_review_queue_command_prints_unreviewed_latest_run(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, _review_queue_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Review Queue" in result.output
    assert "#1" in result.output
    assert "Open Catalyst" in result.output
    assert "Reviewed Catalyst" not in result.output
    assert "record-outcome" in result.output


def test_review_queue_command_uses_requested_run_id(tmp_path: Path) -> None:
    database_path, first, _second = _two_run_database(tmp_path)

    result = runner.invoke(
        app,
        _review_queue_args(database_path, run_id=first.id),
    )

    assert result.exit_code == 0
    assert "First Run Item" in result.output
    assert "Second Run Item" not in result.output


def test_review_queue_command_handles_no_snapshots(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _review_queue_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_review_queue_command_handles_fully_reviewed_run(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        item_name="Reviewed Catalyst",
    )

    result = runner.invoke(app, _review_queue_args(database_path))

    assert result.exit_code == 0
    assert "No unreviewed recommendations found for run #1." in result.output


def test_review_queue_command_rejects_missing_run(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _review_queue_args(tmp_path / "snapshots.db", run_id=99),
    )

    assert result.exit_code != 0
    assert "analysis run #99 was not found" in result.output


def test_review_coverage_command_prints_latest_run_coverage(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, _review_coverage_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Review Coverage" in result.output
    assert "#1" in result.output
    assert "50.0%" in result.output


def test_review_coverage_command_uses_requested_run_id(tmp_path: Path) -> None:
    database_path, first, _second = _two_run_database_with_second_reviewed(tmp_path)

    result = runner.invoke(
        app,
        _review_coverage_args(database_path, run_id=first.id),
    )

    assert result.exit_code == 0
    assert "0.0%" in result.output


def test_review_coverage_command_handles_no_snapshots(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _review_coverage_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
