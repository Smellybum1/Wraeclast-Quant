from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_artifact_helpers import (
    write_invalid_static_site as _write_invalid_static_site,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_command_reports_invalid_static_site_without_failing(
    tmp_path: Path,
) -> None:
    resources_path = _write_manual_resources(tmp_path)
    site_dir = _write_invalid_static_site(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Static site" in result.output
    assert "needs attention" in result.output
    assert "missing markers" in result.output
