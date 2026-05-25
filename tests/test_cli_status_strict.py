from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_strict_allows_missing_optional_artifacts(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            strict=True,
        ),
    )

    assert result.exit_code == 0
    assert "Strict status failed" not in result.output
