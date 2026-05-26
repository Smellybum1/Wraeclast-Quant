from pathlib import Path

from wraeclast_quant.storage.migrations import (
    check_migration_readiness,
    migration_readiness_payload,
)

from database_migration_helpers import write_database_with_backup as _write_database_with_backup


def test_migration_readiness_json_payload_has_stable_keys(tmp_path: Path) -> None:
    database_path, backup_dir, run_id = _write_database_with_backup(tmp_path)

    payload = migration_readiness_payload(check_migration_readiness(database_path, backup_dir))

    assert payload["ready"] is True
    assert payload["schema_version"] == "2"
    assert payload["latest_database_run_id"] == run_id
    assert payload["latest_backup_run_id"] == run_id
    assert isinstance(payload["checks"], list)
    assert payload["blockers"] == []
