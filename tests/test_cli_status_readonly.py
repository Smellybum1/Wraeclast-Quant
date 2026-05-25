from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_command_does_not_create_missing_database(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "missing.db"
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert "No database found." in result.output
    assert "No local database backups found." in result.output
    assert "Database" in result.output
    assert not database_path.exists()
    assert not backup_dir.exists()
