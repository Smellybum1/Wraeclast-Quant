from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def latest_connector_fixture_provenance_database(tmp_path: Path) -> tuple[Path, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="connector-fixture", item_count=1)
    repository.save_run_provenance(
        run.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={"fixture_item_count": 1, "future_cache_path": "data/raw/cache/example.cache"},
    )
    return database_path, run


def two_run_provenance_database(
    tmp_path: Path,
) -> tuple[Path, AnalysisRunRecord, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    first = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    second = repository.create_analysis_run(source_mode="connector-fixture", item_count=1)
    repository.save_run_provenance(
        first.id,
        source_kind="manual",
        resource_name="Manual",
        connector_id="none",
        access_method="manual",
        metadata={"label": "first"},
    )
    repository.save_run_provenance(
        second.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={"label": "second"},
    )
    return database_path, first, second


def missing_provenance_database(tmp_path: Path, *, source_mode: str = "sample-data") -> Path:
    database_path = tmp_path / "snapshots.db"
    SnapshotRepository(database_path).create_analysis_run(source_mode=source_mode, item_count=0)
    return database_path


__all__ = [
    "latest_connector_fixture_provenance_database",
    "missing_provenance_database",
    "two_run_provenance_database",
]
