import sqlite3
from pathlib import Path

import pytest

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    backup_database,
    build_restore_guidance,
    list_database_backups,
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


def test_build_restore_guidance_verifies_backup_without_writing_target(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    target_path = tmp_path / "restored" / "snapshots.db"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    backup = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T00:00:00+00:00",
    )
    assert backup is not None

    guidance = build_restore_guidance(
        backup_path=backup.backup_path,
        database_path=target_path,
    )

    assert guidance.backup_path == backup.backup_path
    assert guidance.database_path == target_path
    assert guidance.latest_run_id == run.id
    assert guidance.latest_run_source_mode == "sample-data"
    assert guidance.latest_run_item_count == len(opportunities)
    assert guidance.target_exists is False
    assert guidance.target_parent_exists is False
    assert "Copy-Item -LiteralPath" in guidance.powershell_command
    assert not target_path.exists()
    assert not target_path.parent.exists()


def test_backup_contract_doc_matches_defaults_and_verification_fields() -> None:
    doc_text = Path("docs/BACKUPS.md").read_text(encoding="utf-8")
    default_paths = _documented_mapping(doc_text, "## Default Paths")
    verification_fields = _documented_bullets(doc_text, "Backup verification reports:")

    assert default_paths["backup_dir"] == str(DEFAULT_BACKUP_DIR).replace("\\", "/")
    assert verification_fields == {
        "schema_version",
        "required_tables",
        "size_bytes",
        "analysis_run_count",
        "scored_opportunity_count",
        "report_artifact_count",
        "recommendation_outcome_count",
        "latest_run_id",
        "latest_run_created_at",
        "latest_run_source_mode",
        "latest_run_item_count",
    }


def _documented_mapping(doc_text: str, heading: str) -> dict[str, str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        key.strip("`"): value.strip("`")
        for key, value in (
            line.strip()[2:].split(": ", 1)
            for line in section.splitlines()
            if line.strip().startswith("- `")
        )
    }


def _documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }
