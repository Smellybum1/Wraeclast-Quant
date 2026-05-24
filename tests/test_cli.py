from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_doc_command_helpers import PUBLIC_COMMANDS as _PUBLIC_COMMANDS
from cli_doc_command_helpers import command_help_args as _command_help_args
from cli_doc_command_helpers import top_level_help_args as _top_level_help_args
from cli_report_helpers import analyze_sample_args as _analyze_sample_args
from cli_readonly_helpers import (
    read_only_missing_database_command_cases as _read_only_missing_database_command_cases,
)
from cli_snapshot_helpers import snapshots_args as _snapshots_args


runner = CliRunner()


def test_top_level_help_lists_public_commands() -> None:
    result = runner.invoke(app, _top_level_help_args())

    assert result.exit_code == 0
    for command in _PUBLIC_COMMANDS:
        assert command in result.output


def test_public_command_help_smoke_matrix() -> None:
    for command in _PUBLIC_COMMANDS:
        result = runner.invoke(app, _command_help_args(command))

        assert result.exit_code == 0, command


def test_snapshots_command_prints_latest_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, _analyze_sample_args(database_path))

    result = runner.invoke(app, _snapshots_args(database_path))

    assert result.exit_code == 0
    assert "Recent Analysis Runs" in result.output
    assert "Stormglass Catalyst" in result.output


def test_read_only_snapshot_commands_do_not_create_missing_database(tmp_path: Path) -> None:
    for index, (command, expected_output) in enumerate(
        _read_only_missing_database_command_cases(tmp_path)
    ):
        database_path = tmp_path / f"missing-{index}" / "snapshots.db"
        result = runner.invoke(
            app,
            [
                *command,
                "--database-path",
                str(database_path),
            ],
        )

        assert result.exit_code == 0
        assert expected_output in result.output
        assert not database_path.exists()
