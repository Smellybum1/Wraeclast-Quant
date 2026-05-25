import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_json_outputs_machine_readable_rows(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            site_dir=tmp_path / "site",
            bundle_dir=tmp_path / "site_bundle",
            json_output=True,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["product"] == "Wraeclast Quant"
    assert payload["schema_version"] == "1.5"
    assert "T" in payload["generated_at"]
    assert payload["strict"] is False
    assert payload["ok"] is True
    assert payload["strict_failures"] == []
    assert payload["strict_failure_keys"] == []
    assert payload["status_counts"] == {"no": 6, "none": 3, "ok": 2}
    rows_by_key = {row["key"]: row for row in payload["rows"]}
    assert payload["rows_by_key"] == rows_by_key
    assert rows_by_key["database_health"]["check"] == "Database health"
    assert payload["rows_by_key"]["public_intel"]["status"] == "no"
    assert payload["rows_by_key"]["safety_boundary"] == {
        "key": "safety_boundary",
        "check": "Safety boundary",
        "status": "ok",
        "details": "Local-only status check; collectors remain dry-run placeholders.",
    }


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
