from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_backup_database_helpers import invalid_backup_dir as _invalid_backup_dir
from cli_database_helpers import sqlite_table_names as _sqlite_table_names
from cli_database_helpers import (
    write_unrelated_sqlite_database as _write_unrelated_sqlite_database,
)
from cli_status_artifact_helpers import (
    write_invalid_market_brief as _write_invalid_market_brief,
    write_invalid_public_intel as _write_invalid_public_intel,
    write_invalid_site_bundle as _write_invalid_site_bundle,
    write_invalid_static_site as _write_invalid_static_site,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import status_workspace as _status_workspace
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


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


def test_status_command_does_not_create_missing_database(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "missing.db"
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert "No database found." in result.output
    assert "No local database backups found." in result.output
    assert "Database" in result.output
    assert not database_path.exists()
    assert not backup_dir.exists()


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


def test_status_command_reports_invalid_public_intel_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=0)
    intel_path = _write_invalid_public_intel(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
        ),
    )

    assert result.exit_code == 0
    assert "Public intel" in result.output
    assert "needs attention" in result.output
    assert "Missing required keys" in result.output


def test_status_strict_exits_nonzero_for_health_failures(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    intel_path = _write_invalid_public_intel(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
        ),
    )

    assert result.exit_code == 1
    assert "Public intel" in result.output
    assert "needs attention" in result.output
    assert "Strict status failed: Public intel" in result.output


def test_status_command_reports_invalid_market_brief_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    brief_path = _write_invalid_market_brief(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            brief_path=brief_path,
        ),
    )

    assert result.exit_code == 0
    assert "Market brief" in result.output
    assert "needs attention" in result.output
    assert "missing markers" in result.output


def test_status_command_reports_invalid_static_site_without_failing(tmp_path: Path) -> None:
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


def test_status_command_reports_invalid_site_bundle_without_failing(tmp_path: Path) -> None:
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
