from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_backup_command_helpers import verify_backup_args as _verify_backup_args
from cli_backup_database_helpers import sample_data_backup as _sample_data_backup


runner = CliRunner()


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
