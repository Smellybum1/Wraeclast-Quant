import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_artifact_helpers import (
    write_stale_public_intel as _write_stale_public_intel,
    write_stale_site_bundle as _write_stale_site_bundle,
    write_stale_static_site as _write_stale_static_site,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_command_helpers import status_json_args as _status_json_args
from cli_status_database_helpers import database_with_two_runs as _database_with_two_runs
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_marks_stale_public_intel_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    intel_path = _write_stale_public_intel(tmp_path, run_id=1)

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["public_intel"]
    assert row["status"] == "needs attention"
    assert (
        "stale; latest database run #2, artifact run #1; run wq export and wq site"
        in row["details"]
    )


def test_status_marks_stale_static_site_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    site_dir = _write_stale_static_site(tmp_path, run_id=1)

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["static_site"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #2, artifact run #1; run wq site" in row["details"]


def test_status_marks_stale_site_bundle_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    bundle_dir = _write_stale_site_bundle(tmp_path, run_id=1)

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            bundle_dir=bundle_dir,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["site_bundle"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #2, bundle run #1; run wq site-bundle" in row[
        "details"
    ]


def test_status_strict_json_exits_nonzero_for_stale_artifacts(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    intel_path = _write_stale_public_intel(tmp_path, run_id=1)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["strict_failures"] == ["Public intel"]
    assert payload["strict_failure_keys"] == ["public_intel"]
    assert payload["rows_by_key"]["public_intel"]["status"] == "needs attention"
