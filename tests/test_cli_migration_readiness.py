import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_backup_command_helpers import migration_readiness_args as _migration_readiness_args
from cli_backup_command_helpers import (
    migration_readiness_json_args as _migration_readiness_json_args,
)
from cli_backup_database_helpers import sample_data_backup as _sample_data_backup


runner = CliRunner()


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
