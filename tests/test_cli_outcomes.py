from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import outcomes_args as _outcomes_args
from cli_outcome_command_helpers import record_outcome_args as _record_outcome_args
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
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
