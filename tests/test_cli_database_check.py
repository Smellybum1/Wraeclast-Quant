from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_backup_command_helpers import db_check_args as _db_check_args
from cli_backup_database_helpers import sample_data_database as _sample_data_database


runner = CliRunner()


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
