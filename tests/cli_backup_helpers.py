from __future__ import annotations

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


__all__ = ["sample_data_backup", "sample_data_database"]
