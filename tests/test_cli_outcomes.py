from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import outcome_review_args as _outcome_review_args
from cli_outcome_command_helpers import outcome_report_args as _outcome_report_args
from cli_outcome_command_helpers import outcomes_args as _outcomes_args
from cli_outcome_command_helpers import record_outcome_args as _record_outcome_args
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
from cli_report_helpers import analyze_sample_args as _analyze_sample_args


runner = CliRunner()


def test_record_outcome_command_saves_manual_outcome(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, _analyze_sample_args(database_path))

    result = runner.invoke(
        app,
        _record_outcome_args(database_path, notes="Reviewed manually."),
    )

    records = SnapshotRepository(database_path).list_recent_outcomes()
    assert result.exit_code == 0
    assert "Recorded positive outcome" in result.output
    assert len(records) == 1
    assert records[0].item_name == "Stormglass Catalyst"
    assert records[0].notes == "Reviewed manually."


def test_record_outcome_command_rejects_missing_item(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, _analyze_sample_args(database_path))

    result = runner.invoke(
        app,
        _record_outcome_args(database_path, item_name="Missing Item"),
    )

    assert result.exit_code != 0
    assert "Missing Item" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_outcomes_command_prints_recent_outcomes_and_summary(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(app, _outcomes_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Outcomes" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Outcome Summary" in result.output
    assert "positive" in result.output


def test_outcomes_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _outcomes_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No recommendation outcomes recorded." in result.output


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


def test_outcome_review_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _outcome_review_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output


def test_outcome_report_command_writes_markdown_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        notes="Manual review.",
    )

    result = runner.invoke(
        app,
        _outcome_report_args(database_path, output_path),
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote outcome review report" in result.output
    assert "# Wraeclast Quant Outcome Review" in report
    assert "Stormglass Catalyst" in report
    assert "Manual review." in report


def test_outcome_report_command_writes_empty_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"

    result = runner.invoke(
        app,
        _outcome_report_args(tmp_path / "snapshots.db", output_path),
    )

    assert result.exit_code == 0
    assert "Wrote empty outcome review report" in result.output
    assert "No reviewed recommendation outcomes found." in output_path.read_text(encoding="utf-8")
