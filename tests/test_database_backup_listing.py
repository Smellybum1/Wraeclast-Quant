import sqlite3
from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import backup_database, list_database_backups
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_list_database_backups_returns_verified_backups_newest_first(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    first = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T00:00:00+00:00",
    )
    second = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T01:00:00+00:00",
    )
    assert first is not None
    assert second is not None

    listings = list_database_backups(backup_dir=backup_dir)

    assert [listing.backup_path for listing in listings] == [
        second.backup_path,
        first.backup_path,
    ]
    assert listings[0].valid is True
    assert listings[0].analysis_run_count == 1
    assert listings[0].latest_run_id == run.id
    assert listings[0].latest_run_source_mode == "sample-data"
    assert listings[0].error == ""


def test_list_database_backups_includes_invalid_backup_without_failing(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    invalid = backup_dir / "invalid.db"
    with sqlite3.connect(invalid) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    listings = list_database_backups(backup_dir=backup_dir)

    assert len(listings) == 1
    assert listings[0].backup_path == invalid
    assert listings[0].valid is False
    assert listings[0].analysis_run_count is None
    assert "missing required tables" in listings[0].error


def test_list_database_backups_missing_directory_returns_empty_without_creating_it(
    tmp_path: Path,
) -> None:
    backup_dir = tmp_path / "missing"

    assert list_database_backups(backup_dir=backup_dir) == []
    assert not backup_dir.exists()
