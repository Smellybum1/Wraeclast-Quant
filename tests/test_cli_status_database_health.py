from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_database_helpers import sqlite_table_names as _sqlite_table_names
from cli_database_helpers import (
    write_unrelated_sqlite_database as _write_unrelated_sqlite_database,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_command_reports_unhealthy_database_without_initializing_schema(
    tmp_path: Path,
) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _write_unrelated_sqlite_database(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
        ),
    )

    assert result.exit_code == 0
    assert "Database health" in result.output
    assert "needs attention" in result.output
    assert "missing tables" in result.output
    assert "Database health check did not pass." in result.output
    assert _sqlite_table_names(database_path) == {"unrelated"}
