import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcomes_args as _record_outcomes_args
from cli_report_helpers import analyze_sample_args as _analyze_sample_args


runner = CliRunner()


def test_record_outcomes_command_rejects_invalid_batch_without_partial_writes(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": "positive"},
                    {"item_name": "Missing Item", "outcome": "negative"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    assert result.exit_code != 0
    assert "Missing Item" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_record_outcomes_command_rejects_already_reviewed_item_without_partial_writes(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    repository = SnapshotRepository(database_path)
    repository.save_recommendation_outcome(1, "Ashen Rune Core", "neutral")
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": "positive"},
                    {"item_name": "Ashen Rune Core", "outcome": "negative"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    records = SnapshotRepository(database_path).list_recent_outcomes(limit=10)
    assert result.exit_code != 0
    assert "already has a recorded outcome" in result.output
    assert len(records) == 1
    assert records[0].item_name == "Ashen Rune Core"
    assert records[0].outcome == "neutral"


def test_record_outcomes_command_dry_run_rejects_invalid_batch_without_writing(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": "positive"},
                    {"item_name": "Missing Item", "outcome": "negative"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _record_outcomes_args(database_path, decisions_path, dry_run=True),
    )

    assert result.exit_code != 0
    assert "Missing Item" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_record_outcomes_command_dry_run_explains_blank_template_outcome(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": ""},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _record_outcomes_args(database_path, decisions_path, dry_run=True),
    )

    assert result.exit_code != 0
    assert "decision 1 for 'Stormglass Catalyst' blank outcome" in result.output
    assert "use: negative, neutral, positive" in result.output
    assert "negative" in result.output
    assert "neutral" in result.output
    assert "positive" in result.output
    assert "record-outcomes --dry-run" in result.output
    assert "Usage:" not in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_record_outcomes_command_dry_run_reports_multiple_template_errors(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": ""},
                    {"item_name": "Ashen Rune Core", "outcome": "maybe"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _record_outcomes_args(database_path, decisions_path, dry_run=True),
    )

    assert result.exit_code != 0
    assert "outcome decisions have 2 validation errors:" in result.output
    assert "decision 1 for 'Stormglass Catalyst' blank outcome" in result.output
    assert (
        "decision 2 for 'Ashen Rune Core' outcome must be one of: "
        "negative, neutral, positive."
    ) in result.output
    assert "Usage:" not in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []
