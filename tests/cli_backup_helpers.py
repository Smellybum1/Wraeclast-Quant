from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.repositories import SnapshotRepository


def sample_data_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=len(opportunities),
    )
    repository.save_scored_opportunities(run.id, opportunities)
    return database_path


def sample_data_backup(tmp_path: Path) -> tuple[Path, Path, Path]:
    database_path = sample_data_database(tmp_path)
    backup_dir = tmp_path / "backups"
    result = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-24T00:00:00+00:00",
    )
    if result is None:
        raise AssertionError("Expected sample database backup to be created.")
    return database_path, backup_dir, result.backup_path


def invalid_backup_dir(tmp_path: Path, *, ensure_new_mtime: bool = False) -> Path:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    invalid_backup = backup_dir / "invalid.db"
    with sqlite3.connect(invalid_backup) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    if ensure_new_mtime:
        time.sleep(0.01)
    return backup_dir


def backup_db_args(database_path: Path, backup_dir: Path) -> list[str]:
    return [
        "backup-db",
        "--database-path",
        str(database_path),
        "--output-dir",
        str(backup_dir),
    ]


def migration_readiness_args(database_path: Path, backup_dir: Path) -> list[str]:
    return [
        "migration-readiness",
        "--database-path",
        str(database_path),
        "--backup-dir",
        str(backup_dir),
    ]


__all__ = [
    "backup_db_args",
    "invalid_backup_dir",
    "migration_readiness_args",
    "sample_data_backup",
    "sample_data_database",
]
