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
