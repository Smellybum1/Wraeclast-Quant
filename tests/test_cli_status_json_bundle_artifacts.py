import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_artifact_helpers import (
    write_stale_site_bundle as _write_stale_site_bundle,
)
from cli_status_command_helpers import status_json_args as _status_json_args
from cli_status_database_helpers import database_with_two_runs as _database_with_two_runs
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


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
