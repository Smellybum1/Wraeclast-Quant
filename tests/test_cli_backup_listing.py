from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_backup_command_helpers import backups_args as _backups_args
from cli_backup_database_helpers import sample_data_backup as _sample_data_backup


runner = CliRunner()


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
