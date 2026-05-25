from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_backup_database_helpers import invalid_backup_dir as _invalid_backup_dir
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_reports_invalid_latest_backup_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    backup_dir = _invalid_backup_dir(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Backups" in result.output
    assert "needs attention" in result.output
    assert "invalid" in result.output
    assert "missing required tables" in result.output


def test_status_strict_exits_nonzero_for_invalid_latest_backup(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    backup_dir = _invalid_backup_dir(tmp_path, ensure_new_mtime=True)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            backup_dir=backup_dir,
            strict=True,
        ),
    )

    assert result.exit_code == 1
    assert "Strict status failed: Backups" in result.output
