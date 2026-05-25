import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import REQUIRED_ARCHIVE_MEMBERS
from wraeclast_quant.reports.site_contract import (
    SITE_CONTRACT_SCHEMA_VERSION,
    write_site_contract,
)

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_site_contract_ready_bundle_writes_versioned_json(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    written_path, payload = write_site_contract(database_path, bundle_dir, output_path)

    persisted = json.loads(written_path.read_text(encoding="utf-8"))
    assert written_path == output_path
    assert persisted == payload
    assert payload["schema_version"] == SITE_CONTRACT_SCHEMA_VERSION
    assert payload["product"] == "Wraeclast Quant"
    assert payload["latest_database_run_id"] == run_id
    assert payload["artifact_run_ids"] == {
        "bundle": run_id,
        "public_intel": run_id,
        "static_site": run_id,
    }
    assert payload["public_intel"]["schema_version"] == "1.0"
    assert payload["bundle"]["bundle_type"] == "local-static-preview"
    assert payload["required_bundle_files"] == sorted(REQUIRED_ARCHIVE_MEMBERS)
    assert payload["publish_readiness"]["ready"] is True
    assert payload["safety"]["derived_only"] is True
    assert payload["safety"]["network_behavior"] == "none"


def test_site_contract_stale_bundle_writes_not_ready_blockers(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(
        tmp_path,
        artifact_run_id=1,
        database_runs=2,
    )
    output_path = tmp_path / "site_contract.json"

    _written_path, payload = write_site_contract(database_path, bundle_dir, output_path)

    assert payload["publish_readiness"]["ready"] is False
    assert payload["latest_database_run_id"] == 2
    assert payload["artifact_run_ids"]["bundle"] == 1
    assert any(
        "latest database run #2, bundle run #1" in blocker
        for blocker in payload["publish_readiness"]["blockers"]
    )


def test_site_contract_missing_bundle_does_not_create_bundle(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"
    output_path = tmp_path / "site_contract.json"

    _written_path, payload = write_site_contract(database_path, missing_dir, output_path)

    assert output_path.exists()
    assert not missing_dir.exists()
    assert payload["publish_readiness"]["ready"] is False
    assert payload["bundle"]["valid"] is False
    assert any("not found" in blocker for blocker in payload["publish_readiness"]["blockers"])


def test_site_contract_invalid_bundle_reports_blockers(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")

    _written_path, payload = write_site_contract(
        database_path,
        bundle_dir,
        tmp_path / "site_contract.json",
    )

    assert payload["publish_readiness"]["ready"] is False
    assert payload["public_intel"]["valid"] is False
    assert any(
        "Public intel contract" in blocker
        for blocker in payload["publish_readiness"]["blockers"]
    )


def test_site_contract_excludes_raw_inputs_and_sensitive_values(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    write_site_contract(database_path, bundle_dir, output_path)

    contract = output_path.read_text(encoding="utf-8")
    forbidden = [
        "raw signal inputs",
        "resource notes:",
        "RESOURCES.md content",
        "secret-token-value",
        "cookie=",
        "api_key=",
        "Stormglass Catalyst inputs",
    ]
    for value in forbidden:
        assert value not in contract
