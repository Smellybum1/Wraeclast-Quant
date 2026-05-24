from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_market_flow_command_helpers import alerts_args as _alerts_args
from cli_market_flow_command_helpers import compare_args as _compare_args
from cli_market_flow_database_helpers import buy_crossing_database as _buy_crossing_database
from cli_market_flow_database_helpers import (
    comparison_database_with_changes as _comparison_database_with_changes,
)
from cli_market_flow_database_helpers import stable_watch_database as _stable_watch_database


runner = CliRunner()


def test_compare_command_prints_delta(tmp_path: Path) -> None:
    database_path = _comparison_database_with_changes(tmp_path)

    result = runner.invoke(app, _compare_args(database_path))

    assert result.exit_code == 0
    assert "Top Movers" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "+26.00" in result.output
    assert "New Catalyst" in result.output
    assert "Removed Relic" in result.output


def test_compare_command_handles_missing_previous_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=0)

    result = runner.invoke(app, _compare_args(database_path))

    assert result.exit_code == 0
    assert "No previous snapshot found for comparison." in result.output


def test_alerts_command_prints_candidates(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)

    result = runner.invoke(app, _alerts_args(database_path))

    assert result.exit_code == 0
    assert "Local Alert Preview" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Score crossed into BUY" in result.output


def test_alerts_command_handles_stable_comparison(tmp_path: Path) -> None:
    database_path = _stable_watch_database(tmp_path)

    result = runner.invoke(app, _alerts_args(database_path))

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output


def test_alerts_command_uses_tuned_thresholds(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)

    result = runner.invoke(
        app,
        _alerts_args(
            database_path,
            watch_threshold=55,
            buy_threshold=90,
            big_delta=100,
        ),
    )

    assert result.exit_code == 0
    assert "Score crossed into WATCH" in result.output
    assert "Score crossed into BUY" not in result.output


def test_alerts_command_rejects_invalid_threshold_order(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _alerts_args(
            tmp_path / "snapshots.db",
            watch_threshold=80,
            buy_threshold=70,
        ),
    )

    assert result.exit_code != 0
    assert "buy_threshold" in result.output
