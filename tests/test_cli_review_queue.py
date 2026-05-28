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


def test_review_queue_command_prints_unreviewed_latest_run(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, _review_queue_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Review Queue" in result.output
    assert "#1" in result.output
    assert "sample-data" in result.output
    assert "local decision-support only" in result.output
    assert "positive=useful signal" in result.output
    assert "Batch review next steps:" in result.output
    assert "wq review-queue --run-id 1 --output-path data/processed/review_queue_run_1.md" in result.output
    assert "wq review-queue --run-id 1 --decisions-output-path data/processed/outcome_decisions_run_1.json" in result.output
    assert "wq record-outcomes --input-path" in result.output
    assert "data/processed/outcome_decisions_run_1.json" in result.output
    assert "--dry-run" in result.output
    assert "Open Catalyst" in result.output
    assert 'wq record-outcome --run-id 1 --item-name "Open Catalyst"' in result.output
    assert "Reviewed Catalyst" not in result.output
    assert "record-outcome" in result.output


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
