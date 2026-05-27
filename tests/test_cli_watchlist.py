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
    assert "Old Catalyst" not in result.output


def test_watchlist_can_select_run_and_limit_results(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    selected = _save_scored_run(
        repository,
        [
            _opportunity("First Choice", 90.0, "BUY"),
            _opportunity("Second Choice", 80.0, "WATCH"),
        ],
        source_mode="manual-import",
    )
    _save_scored_run(
        repository,
        [_opportunity("Latest Choice", 70.0, "WATCH")],
        source_mode="connector-fixture",
    )

    result = runner.invoke(
        app,
        _watchlist_args(repository.database_path, run_id=selected.id, limit=1),
    )

    assert result.exit_code == 0
    assert f"Watchlist - Run #{selected.id} (manual-import)" in result.output
    assert "First Choice" in result.output
    assert "Second Choice" not in result.output
    assert "Latest Choice" not in result.output


def test_watchlist_reports_missing_database(tmp_path: Path) -> None:
    result = runner.invoke(app, _watchlist_args(tmp_path / "missing.db"))

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_watchlist_reports_missing_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    _save_scored_run(repository, [_opportunity("Known Item", 55.0, "WATCH")])

    result = runner.invoke(app, _watchlist_args(repository.database_path, run_id=999))

    assert result.exit_code == 0
    assert "Analysis run #999 was not found." in result.output
