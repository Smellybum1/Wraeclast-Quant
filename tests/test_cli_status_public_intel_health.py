from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_status_artifact_helpers import (
    write_invalid_public_intel as _write_invalid_public_intel,
)
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_command_reports_invalid_public_intel_without_failing(
    tmp_path: Path,
) -> None:
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
