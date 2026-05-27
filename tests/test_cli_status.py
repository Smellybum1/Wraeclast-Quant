from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import status_workspace as _status_workspace


runner = CliRunner()


def test_status_command_prints_local_health(tmp_path: Path) -> None:
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
            backup_dir=workspace.backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Wraeclast Quant Status" in result.output
    assert "Resources" in result.output
    assert "1 configured; 1 automation-eligible" in result.output
    assert "Database health" in result.output
    assert "schema v2" in result.output
    assert "integrity ok" in result.output
    assert "Latest run" in result.output
    assert "#1 sample-data; 2 items" in result.output
    assert "Review coverage" in result.output
    assert "1/2 reviewed" in result.output
    assert "50.0%" in result.output
    assert "wq review-queue" in result.output
    assert "data/processed/review_queue.md" in result.output
    assert "--run-id 1" in result.output
    assert "wq record-outcome" in result.output
    assert "MVP readiness" in result.output
    assert "No-OAuth local loop ready on run #1" in result.output
    assert "Market brief" in result.output
    assert "no snapshot changes" in result.output
    assert "Public intel" in result.output
    assert "schema 1.0" in result.output
    assert "latest run #1" in result.output
    assert "Static site" in result.output
    assert "latest run #1" in result.output
    assert "Site bundle" in result.output
    assert "opportunities" in result.output
    assert "Backups" in result.output
    assert "Backups" in result.output
    assert "ok" in result.output
    assert "latest run #1" in result.output
    assert "collectors remain dry-run placeholders" in result.output
