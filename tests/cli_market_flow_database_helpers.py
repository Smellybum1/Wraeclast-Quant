from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity
from cli_snapshot_helpers import save_scored_run, save_single_opportunity_run


def comparison_database_with_changes(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    save_scored_run(
        repository,
        [
            opportunity("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY"),
            opportunity("Removed Relic", 42.0, "HOLD / SELL SELECTIVELY"),
        ],
    )
    save_scored_run(
        repository,
        [
            opportunity("Stormglass Catalyst", 76.0, "BUY"),
            opportunity("New Catalyst", 60.0, "WATCH"),
        ],
    )
    return database_path


def two_run_item_database(
    tmp_path: Path,
    *,
    item_name: str,
    previous_score: float,
    previous_action: str,
    latest_score: float,
    latest_action: str,
) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    save_single_opportunity_run(
        repository,
        item_name,
        previous_score,
        previous_action,
    )
    save_single_opportunity_run(repository, item_name, latest_score, latest_action)
    return database_path


def buy_crossing_database(tmp_path: Path) -> Path:
    return two_run_item_database(
        tmp_path,
        item_name="Stormglass Catalyst",
        previous_score=50.0,
        previous_action="HOLD / SELL SELECTIVELY",
        latest_score=76.0,
        latest_action="BUY",
    )


def stable_watch_database(tmp_path: Path) -> Path:
    return two_run_item_database(
        tmp_path,
        item_name="Stable Item",
        previous_score=70.0,
        previous_action="WATCH",
        latest_score=70.0,
        latest_action="WATCH",
    )


def small_mover_database(tmp_path: Path) -> Path:
    return two_run_item_database(
        tmp_path,
        item_name="Small Mover",
        previous_score=20.0,
        previous_action="AVOID",
        latest_score=30.0,
        latest_action="AVOID",
    )


def single_buy_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    save_single_opportunity_run(repository, "Stormglass Catalyst", 76.0, "BUY")
    return database_path


__all__ = [
    "buy_crossing_database",
    "comparison_database_with_changes",
    "single_buy_database",
    "small_mover_database",
    "stable_watch_database",
    "two_run_item_database",
]
