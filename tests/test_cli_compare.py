from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_market_flow_command_helpers import compare_args as _compare_args
from cli_market_flow_database_helpers import (
    comparison_database_with_changes as _comparison_database_with_changes,
)


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
