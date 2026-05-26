import json
from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.reports.public_intel import (
    PUBLIC_INTEL_SCHEMA_VERSION,
    build_public_intel,
    write_public_intel,
)

from public_intel_helpers import repository_with_runs as _repository_with_runs
from public_intel_helpers import resources as _resources


def test_public_intel_writes_valid_json(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()
    payload = build_public_intel(
        repository=repository,
        resources=resources,
        assessments=assess_resources(resources),
        generated_at="2026-05-23T00:00:00+00:00",
    )

    assert payload is not None
    output_path = write_public_intel(payload, tmp_path / "public_intel.json")
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded["generated_at"] == "2026-05-23T00:00:00+00:00"
    assert loaded["schema_version"] == PUBLIC_INTEL_SCHEMA_VERSION
    assert loaded["latest_run"]["id"] == 2
