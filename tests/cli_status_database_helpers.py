from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository


def database_with_two_runs(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=1)
    repository.create_analysis_run(source_mode="sample-data", item_count=1)
    return database_path


__all__ = ["database_with_two_runs"]
