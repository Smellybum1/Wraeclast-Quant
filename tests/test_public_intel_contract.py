from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import (
    REQUIRED_TOP_LEVEL_KEYS,
    validate_public_intel_payload,
)
from wraeclast_quant.reports.public_intel import PUBLIC_INTEL_SCHEMA_VERSION

from public_intel_contract_helpers import public_intel_payload as _payload


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
