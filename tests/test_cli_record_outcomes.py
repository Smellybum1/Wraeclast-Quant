import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcomes_args as _record_outcomes_args
from cli_domain_helpers import opportunity as _opportunity
from cli_report_helpers import analyze_sample_args as _analyze_sample_args
from cli_snapshot_helpers import save_scored_run as _save_scored_run


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
    output = " ".join(result.output.split())
    assert result.exit_code == 0
    assert "Recorded 2 outcome(s) for run #1" in output
    assert f"wq review-coverage --database-path {database_path} --run-id 1" in output
    assert f"wq outcomes --database-path {database_path}" in output
    assert f"wq outcome-review --database-path {database_path}" in output
    assert f"wq calibration --database-path {database_path}" in output
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


def test_record_outcomes_command_prints_calibration_prompts_after_success(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    repository = SnapshotRepository(database_path)
    run = _save_scored_run(
        repository,
        [
            _opportunity("Avoid Good", 20.0, "AVOID"),
            _opportunity("Watch Mixed", 60.0, "WATCH"),
        ],
        source_mode="manual-import",
    )
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": run.id,
                "decisions": [
                    {"item_name": "Avoid Good", "outcome": "positive"},
                    {"item_name": "Watch Mixed", "outcome": "neutral"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    assert result.exit_code == 0
    assert "Recorded 2 outcome(s)" in result.output
    assert "Calibration prompts: 2 local read-only prompt(s)." in result.output
    assert "Next: wq calibration" in result.output
    assert "do not retune scoring or change recommendations" in result.output


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

    output = " ".join(result.output.split())
    assert result.exit_code == 0
    assert "Validated 2 outcome decision(s) for run #1" in output
    assert "no records written" in output
    assert (
        f"Next: wq record-outcomes --database-path {database_path} "
        f"--input-path {decisions_path}"
    ) in output
    assert "--dry-run" not in output.split("Next:", 1)[1]
    assert SnapshotRepository(database_path).list_recent_outcomes() == []
