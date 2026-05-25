import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_doc_markdown_helpers import documented_status_row_keys as _documented_status_row_keys
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


def test_status_json_contract_doc_matches_cli_output(tmp_path: Path) -> None:
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

    payload = json.loads(result.output)
    doc_text = Path("docs/STATUS_JSON.md").read_text(encoding="utf-8")
    documented_version = doc_text.split(
        "The current status JSON schema version is `", 1
    )[1].split("`", 1)[0]
    documented_keys = _documented_status_row_keys(doc_text)

    assert result.exit_code == 0
    assert documented_version == payload["schema_version"]
    assert documented_keys == [row["key"] for row in payload["rows"]]
    assert set(documented_keys) == set(payload["rows_by_key"])


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
