import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcome_args as _record_outcome_args
from cli_outcome_command_helpers import record_outcomes_args as _record_outcomes_args
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


def test_record_outcomes_command_saves_human_reviewed_batch(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {
                        "item_name": "Stormglass Catalyst",
                        "outcome": "positive",
                        "notes": "Useful after manual review.",
                    },
                    {
                        "item_name": "Ashen Rune Core",
                        "outcome": "neutral",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    records = SnapshotRepository(database_path).list_recent_outcomes(limit=10)
    assert result.exit_code == 0
    assert "Recorded 2 outcome(s) for run #1" in result.output
    assert "wq review-coverage --run-id 1" in result.output
    assert len(records) == 2
    assert {record.item_name for record in records} == {"Stormglass Catalyst", "Ashen Rune Core"}
    assert {record.outcome for record in records} == {"positive", "neutral"}


def test_record_outcomes_command_ignores_template_metadata(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "local_review_only": True,
                "instructions": "Fill outcomes after human review.",
                "allowed_outcomes": ["positive", "neutral", "negative"],
                "run_id": 1,
                "decisions": [
                    {
                        "item_name": "Stormglass Catalyst",
                        "outcome": "positive",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    records = SnapshotRepository(database_path).list_recent_outcomes(limit=10)
    assert result.exit_code == 0
    assert "Recorded 1 outcome(s) for run #1" in result.output
    assert len(records) == 1
    assert records[0].item_name == "Stormglass Catalyst"


def test_record_outcomes_command_dry_run_validates_without_writing(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {
                        "item_name": "Stormglass Catalyst",
                        "outcome": "positive",
                        "notes": "Useful after manual review.",
                    },
                    {
                        "item_name": "Ashen Rune Core",
                        "outcome": "neutral",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _record_outcomes_args(database_path, decisions_path, dry_run=True),
    )

    assert result.exit_code == 0
    assert "Validated 2 outcome decision(s) for run #1" in result.output
    assert "no records written" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_record_outcomes_command_rejects_invalid_batch_without_partial_writes(tmp_path: Path) -> None:
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
