import sqlite3
from pathlib import Path

import pytest

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import (
    DatabaseBackupError,
    backup_database,
    verify_database_backup,
)
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_backup_database_copies_existing_sqlite_database(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

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


def test_backup_database_rejects_directory_source(tmp_path: Path) -> None:
    with pytest.raises(DatabaseBackupError, match="not a file"):
        backup_database(database_path=tmp_path, output_dir=tmp_path / "backups")


def test_verify_database_backup_reports_counts_and_latest_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=len(opportunities),
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(run.id, opportunities)
    backup = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T01:00:00+00:00",
    )
    assert backup is not None

    verification = verify_database_backup(backup.backup_path)

    assert verification.backup_path == backup.backup_path
    assert verification.schema_version == "2"
    assert verification.required_tables == [
        "analysis_runs",
        "recommendation_outcomes",
        "report_artifacts",
        "run_provenance",
        "scored_opportunities",
    ]
    assert verification.analysis_run_count == 1
    assert verification.scored_opportunity_count == len(opportunities)
    assert verification.report_artifact_count == 0
    assert verification.recommendation_outcome_count == 0
    assert verification.latest_run_id == run.id
    assert verification.latest_run_created_at == "2026-05-23T00:00:00+00:00"
    assert verification.latest_run_source_mode == "sample-data"
    assert verification.latest_run_item_count == len(opportunities)


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
