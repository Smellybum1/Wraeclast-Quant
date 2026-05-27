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


def test_status_strict_flags_stale_stash_ninja_handoff(tmp_path: Path) -> None:
    workspace = _status_workspace(tmp_path)
    payload = json.loads(workspace.stash_ninja_path.read_text(encoding="utf-8"))
    payload["latest_run"]["id"] = 999
    workspace.stash_ninja_path.write_text(json.dumps(payload), encoding="utf-8")

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
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert "stash_ninja_handoff" in payload["strict_failure_keys"]
    row = payload["rows_by_key"]["stash_ninja_handoff"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #1, handoff run #999" in row["details"]


def test_status_strict_allows_missing_stash_ninja_handoff(tmp_path: Path) -> None:
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
            stash_ninja_path=tmp_path / "missing_stash_ninja.json",
            backup_dir=workspace.backup_dir,
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "stash_ninja_handoff" not in payload["strict_failure_keys"]
    row = payload["rows_by_key"]["stash_ninja_handoff"]
    assert row["status"] == "none"
    assert "optional: run wq stash-ninja-watchlist" in row["details"]
