from pathlib import Path

from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.repositories import SnapshotRepository

from database_backup_helpers import sample_database as _sample_database


def test_backup_database_copies_existing_sqlite_database(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    database_path, run, opportunities = _sample_database(tmp_path)

    result = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T00:00:00+00:00",
    )

    assert result is not None
    assert result.source_path == database_path
    assert result.backup_path == backup_dir / "snapshots_20260523T000000Z.db"
    assert result.backup_path.exists()
    assert result.size_bytes > 0
    backup_repository = SnapshotRepository(result.backup_path)
    assert backup_repository.latest_run() == run
    assert len(backup_repository.scored_opportunities_for_run(run.id)) == len(opportunities)


def test_backup_database_missing_source_returns_none_without_creating_output_dir(tmp_path: Path) -> None:
    result = backup_database(
        database_path=tmp_path / "missing" / "snapshots.db",
        output_dir=tmp_path / "backups",
    )

    assert result is None
    assert not (tmp_path / "backups").exists()
