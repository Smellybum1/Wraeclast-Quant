from pathlib import Path

from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.repositories import SnapshotRepository


def write_database_with_backup(tmp_path: Path) -> tuple[Path, Path, int]:
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
