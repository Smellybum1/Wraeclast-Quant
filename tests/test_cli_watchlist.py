from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_report_helpers import watchlist_args as _watchlist_args
from cli_domain_helpers import opportunity as _opportunity
from cli_snapshot_helpers import save_scored_run as _save_scored_run


runner = CliRunner()


def test_watchlist_sample_data_mode() -> None:
    result = runner.invoke(app, _watchlist_args(sample_data=True))

    assert result.exit_code == 0
    assert "Watchlist - Sample Data" in result.output
    assert "Review coverage:" not in result.output


def test_watchlist_defaults_to_latest_stored_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    _save_scored_run(
        repository,
        [_opportunity("Old Catalyst", 40.0, "AVOID")],
        source_mode="sample-data",
    )
    latest = _save_scored_run(
        repository,
        [_opportunity("Fresh Divine", 82.5, "BUY")],
        source_mode="connector-fixture",
    )

    result = runner.invoke(app, _watchlist_args(repository.database_path))

    assert result.exit_code == 0
    assert f"Watchlist - Run #{latest.id} (connector-fixture)" in result.output
    assert "Fresh Divine" in result.output
    assert "Run source: connector-fixture." in result.output
    assert "no trades, whispers, gameplay, publishing, or live collection" in result.output
    assert f"Review coverage: 0/1 reviewed; 1 unreviewed." in result.output
    assert (
        f"wq review-queue --run-id {latest.id} --output-path data/processed/review_queue.md"
        in result.output
    )
    assert (
        f"wq review-queue --run-id {latest.id} --decisions-output-path "
        "data/processed/outcome_decisions.json"
    ) in result.output
    assert "wq record-outcomes --input-path" in result.output
    assert "data/processed/outcome_decisions.json --dry-run" in result.output
    assert "Old Catalyst" not in result.output
