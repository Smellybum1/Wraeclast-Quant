import json
from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import validate_public_intel_file

from public_intel_contract_helpers import public_intel_payload as _payload
from public_intel_contract_helpers import write_public_intel_payload as _write_public_intel_payload


def test_validate_public_intel_file_reports_summary_for_valid_file(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_payload()), encoding="utf-8")

    result = validate_public_intel_file(intel_path)

    assert result.valid is True
    assert result.schema_version == "1.0"
    assert result.latest_run_id == 7
    assert result.top_opportunities_count == 1
    assert result.alerts_count == 1
    assert result.errors == []


def test_validate_public_intel_file_summary_handles_non_int_latest_run_id(
    tmp_path: Path,
) -> None:
    payload = _payload()
    payload["latest_run"]["id"] = "not-a-run-id"
    intel_path = _write_public_intel_payload(tmp_path, payload)

    result = validate_public_intel_file(intel_path)

    assert result.valid is True
    assert result.latest_run_id is None
    assert result.top_opportunities_count == 1
    assert result.alerts_count == 1


def test_validate_public_intel_file_summary_handles_non_object_latest_run(
    tmp_path: Path,
) -> None:
    payload = _payload()
    payload["latest_run"] = []
    intel_path = _write_public_intel_payload(tmp_path, payload)

    result = validate_public_intel_file(intel_path)

    assert result.valid is False
    assert result.latest_run_id is None
    assert result.top_opportunities_count == 1
    assert result.alerts_count == 1
    assert "latest_run must be an object." in result.errors


def test_validate_public_intel_file_summary_counts_non_list_collections_as_zero(
    tmp_path: Path,
) -> None:
    payload = _payload()
    payload["top_opportunities"] = {"item_name": "Stormglass Catalyst"}
    payload["alerts"] = {"item_name": "Stormglass Catalyst"}
    intel_path = _write_public_intel_payload(tmp_path, payload)

    result = validate_public_intel_file(intel_path)

    assert result.valid is False
    assert result.latest_run_id == 7
    assert result.top_opportunities_count == 0
    assert result.alerts_count == 0
    assert "top_opportunities must be a list." in result.errors
    assert "alerts must be a list." in result.errors
