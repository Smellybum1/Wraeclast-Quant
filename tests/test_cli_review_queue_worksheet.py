import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity
from cli_outcome_command_helpers import review_queue_args as _review_queue_args
from cli_outcome_database_helpers import (
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)


runner = CliRunner()


def test_review_queue_command_writes_local_review_worksheet(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    output_path = tmp_path / "review_queue.md"

    result = runner.invoke(app, _review_queue_args(database_path, output_path=output_path))

    assert result.exit_code == 0
    assert "Wrote review queue worksheet" in result.output
    worksheet = output_path.read_text(encoding="utf-8")
    assert "# Wraeclast Quant Review Queue" in worksheet
    assert "Local review worksheet only. No outcome decisions have been recorded." in worksheet
    assert "Run source: sample-data." in worksheet
    assert "| Open Catalyst | 60.00 | WATCH | positive / neutral / negative |" in worksheet
    assert '`wq record-outcome --run-id 1 --item-name "Open Catalyst"' in worksheet
    assert "--outcome <decision>" in worksheet
    assert "## Outcome Command Options" in worksheet
    assert "## Review Checklist" in worksheet
    assert "Inspect each item in your local market context" in worksheet
    assert "wq review-coverage --run-id 1" in worksheet
    assert "### Open Catalyst" in worksheet
    assert '`positive`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome positive`' in worksheet
    assert '`neutral`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome neutral`' in worksheet
    assert '`negative`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome negative`' in worksheet
    assert "## Manual Review Notes" in worksheet
    assert "- Open Catalyst:" in worksheet
    assert "  - Local notes:" in worksheet
    assert 'append --notes "<local note>"' in worksheet
    assert "Reviewed Catalyst" not in worksheet


def test_review_queue_worksheet_can_include_local_context(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    output_path = tmp_path / "review_queue.md"
    context_path = tmp_path / "ui_observation_review.md"
    context_path.write_text(
        "# Currency Exchange UI Observation Review Notes\n\n"
        "| Pair | Market ratio | Visible stock |\n"
        "| --- | --- | ---: |\n"
        "| Open Catalyst | 30:1 | 42,000 |\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        _review_queue_args(
            database_path,
            output_path=output_path,
            context_path=context_path,
        ),
    )

    worksheet = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "## Local Review Context" in worksheet
    assert "Included from a user-supplied local context file" in worksheet
    assert "# Currency Exchange UI Observation Review Notes" in worksheet
    assert "| Open Catalyst | 30:1 | 42,000 |" in worksheet
    assert "## Outcome Labels" in worksheet


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
    assert payload == {
        "run_id": 1,
        "decisions": [
            {
                "item_name": "Open Catalyst",
                "outcome": "",
                "notes": "",
            }
        ],
    }


def test_review_queue_context_path_requires_output_path(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)
    context_path = tmp_path / "context.md"
    context_path.write_text("local context", encoding="utf-8")

    result = runner.invoke(app, _review_queue_args(database_path, context_path=context_path))

    assert result.exit_code != 0
    assert "Use --context-path together with --output-path." in result.output


def test_review_queue_worksheet_escapes_markdown_and_commands(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    output_path = tmp_path / "review_queue.md"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run("sample-data", item_count=1)
    repository.save_scored_opportunities(
        run.id,
        [
            opportunity('Open | ` "Catalyst"', 60.0, "WATCH"),
        ],
    )

    result = runner.invoke(app, _review_queue_args(database_path, output_path=output_path))

    assert result.exit_code == 0
    worksheet = output_path.read_text(encoding="utf-8")
    assert 'Open \\| ` "Catalyst"' in worksheet
    assert '--item-name "Open \\| `` `"Catalyst`""' in worksheet
