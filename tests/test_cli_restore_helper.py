from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_backup_command_helpers import restore_helper_args as _restore_helper_args
from cli_backup_database_helpers import sample_data_backup as _sample_data_backup


runner = CliRunner()


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
