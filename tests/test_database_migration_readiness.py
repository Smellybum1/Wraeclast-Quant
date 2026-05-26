import sqlite3
from pathlib import Path

from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.migrations import (
    check_migration_readiness,
    migration_readiness_payload,
)
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_migration_readiness_ready_with_fresh_verified_backup(tmp_path: Path) -> None:
    database_path, backup_dir, run_id = _write_database_with_backup(tmp_path)

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is True
    assert result.schema_version == "2"
    assert result.latest_database_run_id == run_id
    assert result.latest_backup_run_id == run_id
    assert result.blockers == []
    assert {row.key: row.status for row in result.checks}["migration_readiness"] == "ready"


def test_migration_readiness_missing_database_is_non_mutating(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    backup_dir = tmp_path / "backups"

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is False
    assert any("No database found" in blocker for blocker in result.blockers)
    assert not database_path.exists()
    assert not database_path.parent.exists()
    assert not backup_dir.exists()


def test_migration_readiness_missing_backup_reports_blocker(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "missing_backups"
    SnapshotRepository(database_path).create_analysis_run(
        source_mode="sample-data",
        item_count=1,
    )

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is False
    assert any("No local SQLite backups found" in blocker for blocker in result.blockers)
    assert not backup_dir.exists()


def test_migration_readiness_stale_backup_reports_blocker(tmp_path: Path) -> None:
    database_path, backup_dir, run_id = _write_database_with_backup(tmp_path)
    SnapshotRepository(database_path).create_analysis_run(
        source_mode="manual-import",
        item_count=1,
    )

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is False
    assert result.latest_database_run_id == run_id + 1
    assert result.latest_backup_run_id == run_id
    assert any(
        "latest database run #2, latest backup run #1" in blocker
        for blocker in result.blockers
    )


def test_migration_readiness_invalid_backup_reports_blocker(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    SnapshotRepository(database_path).create_analysis_run(
        source_mode="sample-data",
        item_count=1,
    )
    with sqlite3.connect(backup_dir / "invalid.db") as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is False
    assert any("missing required tables" in blocker for blocker in result.blockers)


def test_migration_readiness_json_payload_has_stable_keys(tmp_path: Path) -> None:
    database_path, backup_dir, run_id = _write_database_with_backup(tmp_path)

    payload = migration_readiness_payload(check_migration_readiness(database_path, backup_dir))

    assert payload["ready"] is True
    assert payload["schema_version"] == "2"
    assert payload["latest_database_run_id"] == run_id
    assert payload["latest_backup_run_id"] == run_id
    assert isinstance(payload["checks"], list)
    assert payload["blockers"] == []


def _write_database_with_backup(tmp_path: Path) -> tuple[Path, Path, int]:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    backup = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T00:00:00+00:00",
    )
    assert backup is not None
    return database_path, backup_dir, run.id
