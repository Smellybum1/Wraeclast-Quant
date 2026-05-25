from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_backup_command_helpers import backup_db_args as _backup_db_args
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
