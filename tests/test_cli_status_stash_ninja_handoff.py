import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import status_workspace as _status_workspace


runner = CliRunner()


def test_status_reports_fresh_stash_ninja_handoff(tmp_path: Path) -> None:
    workspace = _status_workspace(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=workspace.database_path,
            resources_path=workspace.resources_path,
            brief_path=workspace.brief_path,
            intel_path=workspace.intel_path,
            site_dir=workspace.site_dir,
            bundle_dir=workspace.bundle_dir,
            stash_ninja_path=workspace.stash_ninja_path,
            backup_dir=workspace.backup_dir,
            json_output=True,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["stash_ninja_handoff"]
    assert row["status"] == "ok"
    assert "schema 1.0" in row["details"]
    assert "latest run #1" in row["details"]
    assert "manual-only companion handoff" in row["details"]
