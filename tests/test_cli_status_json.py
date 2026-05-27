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
    assert payload["status_counts"] == {"no": 6, "none": 4, "ok": 2}
    rows_by_key = {row["key"]: row for row in payload["rows"]}
    assert payload["rows_by_key"] == rows_by_key
    assert rows_by_key["database_health"]["check"] == "Database health"
    assert rows_by_key["mvp_readiness"]["status"] == "none"
    assert "wq daily --input-path" in rows_by_key["mvp_readiness"]["details"]
    assert payload["rows_by_key"]["public_intel"]["status"] == "no"
    assert payload["rows_by_key"]["safety_boundary"] == {
        "key": "safety_boundary",
        "check": "Safety boundary",
        "status": "ok",
        "details": "Local-only status check; collectors remain dry-run placeholders.",
    }
