import json
from pathlib import Path

import pytest

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    REQUIRED_TOP_LEVEL_KEYS,
    validate_public_intel_file,
    validate_public_intel_payload,
)
from wraeclast_quant.reports.public_intel import PUBLIC_INTEL_SCHEMA_VERSION


def test_validate_public_intel_payload_accepts_v1_contract() -> None:
    assert validate_public_intel_payload(_payload()) == []


def test_validate_public_intel_payload_rejects_wrong_schema_version() -> None:
    payload = _payload()
    payload["schema_version"] = "2.0"

    errors = validate_public_intel_payload(payload)

    assert any("schema_version must be 1.0" in error for error in errors)


def test_validate_public_intel_payload_rejects_missing_required_keys() -> None:
    payload = _payload()
    del payload["latest_run"]

    errors = validate_public_intel_payload(payload)

    assert "Missing required keys: latest_run" in errors


def test_validate_public_intel_payload_rejects_raw_inputs_notes_and_urls() -> None:
    payload = _payload()
    payload["top_opportunities"][0]["inputs"] = {"demand_momentum": 88}
    payload["alerts"][0]["notes"] = "private note"
    payload["compliance_summary"]["url"] = "https://example.test/source"

    errors = validate_public_intel_payload(payload)

    assert any("$.top_opportunities[0].inputs" in error for error in errors)
    assert any("$.alerts[0].notes" in error for error in errors)
    assert any("$.compliance_summary.url" in error for error in errors)
    assert any("Raw URL" in error for error in errors)


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


def test_validate_public_intel_file_rejects_missing_file_without_creating_it(tmp_path: Path) -> None:
    intel_path = tmp_path / "missing" / "public_intel.json"

    with pytest.raises(PublicIntelContractError, match="Public intel file not found"):
        validate_public_intel_file(intel_path)

    assert not intel_path.exists()
    assert not intel_path.parent.exists()


def test_validate_public_intel_file_rejects_invalid_json(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(PublicIntelContractError, match="Invalid public intel JSON"):
        validate_public_intel_file(intel_path)


def test_public_intel_contract_doc_matches_validator() -> None:
    doc_text = Path("docs/PUBLIC_INTEL_JSON.md").read_text(encoding="utf-8")
    documented_version = doc_text.split(
        "The current public intel schema version is `", 1
    )[1].split("`", 1)[0]
    documented_fields_section = doc_text.split("Required top-level fields:\n\n", 1)[
        1
    ].split("\n\n", 1)[0]
    documented_fields = {
        line.strip()[3:-1]
        for line in documented_fields_section.splitlines()
        if line.strip().startswith("- `")
    }

    assert documented_version == PUBLIC_INTEL_SCHEMA_VERSION
    assert documented_fields == REQUIRED_TOP_LEVEL_KEYS


def _write_public_intel_payload(tmp_path: Path, payload: dict[str, object]) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    return intel_path


def _payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": 7,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        "recent_runs": [
            {
                "id": 7,
                "created_at": "2026-05-23T00:00:00+00:00",
                "source_mode": "sample-data",
                "item_count": 1,
            }
        ],
        "top_opportunities": [
            {
                "item_name": "Stormglass Catalyst",
                "opportunity_score": 76.0,
                "action": "BUY",
            }
        ],
        "score_trends": [
            {
                "item_name": "Stormglass Catalyst",
                "points": [{"run_id": 7, "score": 76.0, "action": "BUY"}],
            }
        ],
        "snapshot_changes": {
            "previous_run_id": None,
            "latest_run_id": 7,
            "top_movers": [],
            "status_changes": [],
        },
        "alerts": [
            {
                "severity": "high",
                "item_name": "Stormglass Catalyst",
                "reason": "Score crossed into BUY",
                "latest_score": 76.0,
                "score_delta": 26.0,
            }
        ],
        "outcome_summary": {"positive": 0, "neutral": 0, "negative": 0},
        "review_coverage": {
            "run_id": 7,
            "total_recommendations": 1,
            "reviewed_recommendations": 0,
            "unreviewed_recommendations": 1,
            "reviewed_percent": 0.0,
        },
        "compliance_summary": {
            "total_resources": 1,
            "status_counts": {"manual-review": 1},
            "automation_eligible_count": 0,
        },
    }
