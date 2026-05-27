from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity
from cli_outcome_command_helpers import review_queue_args as _review_queue_args
from cli_outcome_database_helpers import (
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)
from cli_outcome_database_helpers import two_run_database as _two_run_database


runner = CliRunner()


def test_review_queue_command_prints_unreviewed_latest_run(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, _review_queue_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Review Queue" in result.output
    assert "#1" in result.output
    assert "sample-data" in result.output
    assert "local decision-support only" in result.output
    assert "positive=useful signal" in result.output
    assert "Open Catalyst" in result.output
    assert 'wq record-outcome --run-id 1 --item-name "Open Catalyst"' in result.output
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
    assert "### Open Catalyst" in worksheet
    assert '`positive`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome positive`' in worksheet
    assert '`neutral`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome neutral`' in worksheet
    assert '`negative`: `wq record-outcome --run-id 1 --item-name "Open Catalyst" --outcome negative`' in worksheet
    assert "## Manual Review Notes" in worksheet
    assert "- Open Catalyst:" in worksheet
    assert "  - Local notes:" in worksheet
    assert 'append --notes "<local note>"' in worksheet
    assert "Reviewed Catalyst" not in worksheet


def test_review_queue_command_rejects_missing_run(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _review_queue_args(tmp_path / "snapshots.db", run_id=99),
    )

    assert result.exit_code != 0
    assert "analysis run #99 was not found" in result.output


def test_review_queue_command_escapes_item_names_in_command_templates(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run("sample-data", item_count=2)
    repository.save_scored_opportunities(
        run.id,
        [
            opportunity('Reviewed ` "Catalyst"', 76.0, "BUY"),
            opportunity('Open ` "Catalyst"', 60.0, "WATCH"),
        ],
    )
    repository.save_recommendation_outcome(run.id, 'Reviewed ` "Catalyst"', "positive")

    result = runner.invoke(app, _review_queue_args(database_path))

    assert result.exit_code == 0
    assert '--item-name "Open `` `"Catalyst`""' in result.output


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
