import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.db import connect
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcomes_args as _record_outcomes_args
from cli_report_helpers import analyze_sample_args as _analyze_sample_args


runner = CliRunner()


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
    assert "wq outcomes, wq outcome-review, and wq calibration" in result.output
    assert len(records) == 2
    assert {record.item_name for record in records} == {
        "Stormglass Catalyst",
        "Ashen Rune Core",
    }
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
                        "action": "WATCH",
                        "item_name": "Stormglass Catalyst",
                        "opportunity_score": 60.0,
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
    assert f"Next: wq record-outcomes --input-path {decisions_path}" in result.output
    assert "--dry-run" not in result.output.split("Next:", 1)[1]
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


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


def test_record_outcomes_command_rolls_back_if_batch_write_fails(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_ashen_rune_core_outcome
            BEFORE INSERT ON recommendation_outcomes
            WHEN NEW.item_name = 'Ashen Rune Core'
            BEGIN
                SELECT RAISE(ABORT, 'blocked batch insert');
            END;
            """
        )
        connection.commit()
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

    assert result.exit_code != 0
    assert "could not record outcome batch" in result.output
    assert "no records written" in result.output
    assert "blocked batch insert" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes(limit=10) == []


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
