import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_public_artifact_file_helpers import (
    write_publish_ready_bundle as _write_publish_ready_bundle,
)
from cli_public_artifact_publish_command_helpers import (
    publish_check_args as _publish_check_args,
)


runner = CliRunner()


def test_publish_check_ready_bundle_prints_readiness(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)

    result = runner.invoke(
        app,
        _publish_check_args(database_path, bundle_dir),
    )

    assert result.exit_code == 0
    assert "Local Publish Readiness" in result.output
    assert "Manual publishing readiness" in result.output
    assert "ready" in result.output
    assert "Publish check is local-only" in result.output


def test_publish_check_json_outputs_stable_fields(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    result = runner.invoke(
        app,
        _publish_check_args(database_path, bundle_dir, json_output=True),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ready"] is True
    assert payload["latest_database_run_id"] == run_id
    assert payload["bundle_latest_run_id"] == run_id
    assert payload["blockers"] == []
    assert isinstance(payload["checks"], list)


def test_publish_check_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    SnapshotRepository(database_path).create_analysis_run(
        source_mode="sample-data",
        item_count=1,
    )
    missing_bundle = tmp_path / "missing_bundle"

    result = runner.invoke(
        app,
        _publish_check_args(database_path, missing_bundle, strict=True),
    )

    assert result.exit_code == 1
    assert "not found" in result.output
    assert not missing_bundle.exists()
