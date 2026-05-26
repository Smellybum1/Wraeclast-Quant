import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_json_strict_exits_nonzero_with_parseable_failures(
    tmp_path: Path,
) -> None:
    resources_path = _write_manual_resources(tmp_path)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["schema_version"] == "1.5"
    assert "generated_at" in payload
    assert payload["strict"] is True
    assert payload["ok"] is False
    assert payload["status_counts"]["needs_attention"] == 1
    assert payload["strict_failures"] == ["Public intel"]
    assert payload["strict_failure_keys"] == ["public_intel"]
    assert payload["rows_by_key"]["public_intel"]["status"] == "needs attention"
    assert "Strict status failed" not in result.output
