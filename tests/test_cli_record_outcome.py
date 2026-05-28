from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcome_args as _record_outcome_args
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
    assert "wq review-coverage --run-id 1" in result.output
    assert "wq outcomes, wq outcome-review, and wq calibration" in result.output
    assert "wq export, wq site, and wq site-bundle" in result.output
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


def test_record_outcome_command_rejects_duplicate_item_outcome(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, _analyze_sample_args(database_path))
    first = runner.invoke(app, _record_outcome_args(database_path))

    result = runner.invoke(
        app,
        _record_outcome_args(database_path, outcome="neutral"),
    )

    records = SnapshotRepository(database_path).list_recent_outcomes()
    assert first.exit_code == 0
    assert result.exit_code != 0
    assert "already has a recorded outcome" in result.output
    assert len(records) == 1
    assert records[0].outcome == "positive"
