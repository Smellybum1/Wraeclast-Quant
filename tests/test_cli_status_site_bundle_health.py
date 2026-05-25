from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_artifact_helpers import (
    write_invalid_site_bundle as _write_invalid_site_bundle,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_command_reports_invalid_site_bundle_without_failing(
    tmp_path: Path,
) -> None:
    resources_path = _write_manual_resources(tmp_path)
    bundle_dir = _write_invalid_site_bundle(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            bundle_dir=bundle_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Site bundle" in result.output
    assert "needs attention" in result.output
    assert "manifest.json is missing" in result.output
    assert "not a valid zip file" in result.output
