from pathlib import Path

from wraeclast_quant.storage.migrations import check_migration_readiness

from database_migration_helpers import write_database_with_backup as _write_database_with_backup


def test_migration_readiness_ready_with_fresh_verified_backup(tmp_path: Path) -> None:
    database_path, backup_dir, run_id = _write_database_with_backup(tmp_path)

    result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)

    assert result.ready is True
    assert result.schema_version == "2"
    assert result.latest_database_run_id == run_id
    assert result.latest_backup_run_id == run_id
    assert result.blockers == []
    assert {row.key: row.status for row in result.checks}["migration_readiness"] == "ready"
