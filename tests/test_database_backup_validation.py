import sqlite3
from pathlib import Path

import pytest

from wraeclast_quant.storage.backups import (
    DatabaseBackupError,
    backup_database,
    verify_database_backup,
)


def test_backup_database_rejects_directory_source(tmp_path: Path) -> None:
    with pytest.raises(DatabaseBackupError, match="not a file"):
        backup_database(database_path=tmp_path, output_dir=tmp_path / "backups")


def test_verify_database_backup_rejects_missing_file_without_creating_it(tmp_path: Path) -> None:
    backup_path = tmp_path / "missing" / "backup.db"

    with pytest.raises(DatabaseBackupError, match="Backup file not found"):
        verify_database_backup(backup_path)

    assert not backup_path.exists()
    assert not backup_path.parent.exists()


def test_verify_database_backup_rejects_sqlite_without_required_tables(tmp_path: Path) -> None:
    backup_path = tmp_path / "not_wq.db"
    with sqlite3.connect(backup_path) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    with pytest.raises(DatabaseBackupError, match="missing required tables"):
        verify_database_backup(backup_path)
