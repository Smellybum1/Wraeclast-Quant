import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity as _opportunity
from cli_snapshot_helpers import save_scored_run as _save_scored_run
from cli_stash_ninja_helpers import stash_ninja_args as _stash_ninja_args


runner = CliRunner()


def test_stash_ninja_watchlist_can_select_run_and_score_threshold(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    selected = _save_scored_run(
        repository,
        [
            _opportunity("Selected Watch", 60.0, "WATCH"),
            _opportunity("Selected Skip", 54.0, "HOLD / SELL SELECTIVELY"),
        ],
        source_mode="manual-import",
    )
    _save_scored_run(
        repository,
        [_opportunity("Latest Item", 90.0, "BUY")],
        source_mode="connector-fixture",
    )
    output_path = tmp_path / "selected.json"

    result = runner.invoke(
        app,
        _stash_ninja_args(
            repository.database_path,
            output_path,
            run_id=selected.id,
            min_score=55.0,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["latest_run"]["id"] == selected.id
    assert [item["item_name"] for item in payload["items"]] == ["Selected Watch"]


def test_stash_ninja_watchlist_reports_missing_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _stash_ninja_args(tmp_path / "missing.db", tmp_path / "stash_ninja.json"),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_stash_ninja_watchlist_reports_missing_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    _save_scored_run(repository, [_opportunity("Known Item", 60.0, "WATCH")])

    result = runner.invoke(
        app,
        _stash_ninja_args(repository.database_path, tmp_path / "stash_ninja.json", run_id=99),
    )

    assert result.exit_code == 0
    assert "Analysis run #99 was not found." in result.output
