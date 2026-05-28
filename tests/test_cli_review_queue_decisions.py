import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import review_queue_args as _review_queue_args
from cli_outcome_database_helpers import (
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)


runner = CliRunner()


def test_review_queue_command_writes_outcome_decisions_template(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    decisions_path = tmp_path / "outcome_decisions.json"

    result = runner.invoke(
        app,
        _review_queue_args(
            database_path,
            decisions_output_path=decisions_path,
        ),
    )

    payload = json.loads(decisions_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert "Wrote outcome decisions template" in result.output
    assert f"wq record-outcomes --input-path {decisions_path} --dry-run" in result.output
    assert payload == {
        "allowed_outcomes": ["positive", "neutral", "negative"],
        "instructions": (
            "Fill each outcome with one of: positive, neutral, negative. "
            "Then run record-outcomes --dry-run before recording."
        ),
        "local_review_only": True,
        "run_id": 1,
        "decisions": [
            {
                "action": "WATCH",
                "item_name": "Open Catalyst",
                "outcome": "",
                "opportunity_score": 60.0,
                "notes": "",
            }
        ],
    }


def test_review_queue_decisions_template_overwrites_blank_template(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    decisions_path = tmp_path / "outcome_decisions.json"
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Old Item", "outcome": "", "notes": ""},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _review_queue_args(
            database_path,
            decisions_output_path=decisions_path,
        ),
    )

    payload = json.loads(decisions_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert payload["decisions"][0]["item_name"] == "Open Catalyst"


def test_review_queue_decisions_template_refuses_to_overwrite_reviewed_labels(
    tmp_path: Path,
) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    decisions_path = tmp_path / "outcome_decisions.json"
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {
                        "item_name": "Open Catalyst",
                        "outcome": "neutral",
                        "notes": "human label",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _review_queue_args(
            database_path,
            decisions_output_path=decisions_path,
        ),
    )

    payload = json.loads(decisions_path.read_text(encoding="utf-8"))
    assert result.exit_code != 0
    assert "refusing to overwrite local review work" in result.output
    assert payload["decisions"][0]["outcome"] == "neutral"
    assert payload["decisions"][0]["notes"] == "human label"
