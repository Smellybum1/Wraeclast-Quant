import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_backup_command_helpers import backup_db_args as _backup_db_args
from cli_backup_command_helpers import backups_args as _backups_args
from cli_backup_command_helpers import db_check_args as _db_check_args
from cli_backup_command_helpers import migration_readiness_args as _migration_readiness_args
from cli_backup_command_helpers import (
    migration_readiness_json_args as _migration_readiness_json_args,
)
from cli_backup_command_helpers import restore_helper_args as _restore_helper_args
from cli_backup_command_helpers import verify_backup_args as _verify_backup_args
from cli_backup_database_helpers import sample_data_backup as _sample_data_backup
from cli_backup_database_helpers import sample_data_database as _sample_data_database


runner = CliRunner()


def test_backup_db_command_writes_local_backup(tmp_path: Path) -> None:
    database_path = _sample_data_database(tmp_path)
    backup_dir = tmp_path / "backups"

    result = runner.invoke(
        app,
        _backup_db_args(database_path, backup_dir),
    )

    backups = list(backup_dir.glob("snapshots_*.db"))
    assert result.exit_code == 0
    assert "Local SQLite Backup" in result.output
    assert "local-only" in result.output
    assert "Verified" in result.output
    assert "Schema version" in result.output
    assert "Analysis runs" in result.output
    assert "Latest source" in result.output
    assert "sample-data" in result.output
    assert len(backups) == 1
    assert SnapshotRepository(backups[0]).latest_run() is not None


def test_backup_db_command_handles_missing_database_without_creating_output_dir(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    backup_dir = tmp_path / "backups"

    result = runner.invoke(
        app,
        _backup_db_args(database_path, backup_dir),
    )

    assert result.exit_code == 0
    assert "No database found to back up." in result.output
    assert not database_path.exists()
    assert not backup_dir.exists()


def test_verify_backup_command_prints_counts(tmp_path: Path) -> None:
    _database_path, _backup_dir, backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(app, _verify_backup_args(backup_path))

    assert result.exit_code == 0
    assert "SQLite Backup Verification" in result.output
    assert "Schema version" in result.output
    assert "Required table names" in result.output
    assert "Analysis runs" in result.output
    assert "Scored opportunities" in result.output
    assert "10" in result.output
    assert "read-only" in result.output


def test_verify_backup_command_rejects_missing_file_without_creating_it(tmp_path: Path) -> None:
    backup_path = tmp_path / "missing" / "backup.db"

    result = runner.invoke(app, _verify_backup_args(backup_path))

    assert result.exit_code != 0
    assert "Backup file not found" in result.output
    assert not backup_path.exists()
    assert not backup_path.parent.exists()


def test_db_check_command_prints_database_health(tmp_path: Path) -> None:
    database_path = _sample_data_database(tmp_path)

    result = runner.invoke(app, _db_check_args(database_path))

    assert result.exit_code == 0
    assert "SQLite Database Check" in result.output
    assert "Schema version" in result.output
    assert "Required table names" in result.output
    assert "Integrity" in result.output
    assert "Required tables" in result.output
    assert "Analysis runs" in result.output
    assert "Latest source" in result.output
    assert "sample-data" in result.output
    assert "read-only" in result.output


def test_db_check_command_handles_missing_database_without_creating_it(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, _db_check_args(database_path))

    assert result.exit_code == 0
    assert "No database found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_backups_command_lists_local_backups(tmp_path: Path) -> None:
    _database_path, backup_dir, _backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(app, _backups_args(backup_dir))

    assert result.exit_code == 0
    assert "Local SQLite Backups" in result.output
    assert "valid" in result.output
    assert "snapshots_" in result.output
    assert "sample-data" in result.output
    assert "read-only" in result.output


def test_backups_command_handles_missing_directory_without_creating_it(tmp_path: Path) -> None:
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(app, _backups_args(backup_dir))

    assert result.exit_code == 0
    assert "No database backups found." in result.output
    assert not backup_dir.exists()


def test_restore_helper_prints_manual_restore_command_without_writing_target(tmp_path: Path) -> None:
    _database_path, _backup_dir, backup_path = _sample_data_backup(tmp_path)
    target_path = tmp_path / "restore" / "snapshots.db"

    result = runner.invoke(
        app,
        _restore_helper_args(backup_path, target_path),
    )

    assert result.exit_code == 0
    assert "SQLite Restore Helper" in result.output
    assert "Manual PowerShell restore command" in result.output
    assert "Copy-Item -LiteralPath" in result.output
    assert "Restore helper is read-only" in result.output
    assert not target_path.exists()
    assert not target_path.parent.exists()


def test_restore_helper_rejects_missing_backup_without_creating_target(tmp_path: Path) -> None:
    backup_path = tmp_path / "missing" / "backup.db"
    target_path = tmp_path / "restore" / "snapshots.db"

    result = runner.invoke(
        app,
        _restore_helper_args(backup_path, target_path),
    )

    assert result.exit_code != 0
    assert "Backup file not found" in result.output
    assert not backup_path.exists()
    assert not backup_path.parent.exists()
    assert not target_path.exists()
    assert not target_path.parent.exists()


def test_migration_readiness_command_prints_table(tmp_path: Path) -> None:
    database_path, backup_dir, _backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(
        app,
        _migration_readiness_args(database_path, backup_dir),
    )

    assert result.exit_code == 0
    assert "SQLite Migration Readiness" in result.output
    assert "Migration readiness" in result.output
    assert "ready" in result.output


def test_migration_readiness_json_outputs_stable_fields(tmp_path: Path) -> None:
    database_path, backup_dir, _backup_path = _sample_data_backup(tmp_path)
    run = SnapshotRepository(database_path).latest_run()

    result = runner.invoke(
        app,
        _migration_readiness_json_args(database_path, backup_dir),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ready"] is True
    assert payload["schema_version"] == "2"
    assert run is not None
    assert payload["latest_database_run_id"] == run.id
    assert payload["latest_backup_run_id"] == run.id
    assert payload["blockers"] == []
    assert isinstance(payload["checks"], list)


def test_migration_readiness_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(
        app,
        [
            "migration-readiness",
            "--strict",
            "--database-path",
            str(database_path),
            "--backup-dir",
            str(backup_dir),
        ],
    )

    assert result.exit_code == 1
    assert "not ready" in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()
    assert not backup_dir.exists()
