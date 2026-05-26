import json
from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.reports.public_intel import build_public_intel

from public_intel_helpers import repository_with_runs as _repository_with_runs
from public_intel_helpers import resources as _resources


def test_public_intel_includes_compliance_summary(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["compliance_summary"]["total_resources"] == 3
    assert payload["compliance_summary"]["automation_eligible_count"] == 1
    assert payload["compliance_summary"]["status_counts"]["approved-api"] == 1
    assert payload["compliance_summary"]["status_counts"]["manual-review"] == 1
    assert payload["compliance_summary"]["status_counts"]["needs-review"] == 1


def test_public_intel_excludes_raw_inputs_and_resource_notes(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    encoded = json.dumps(payload)
    assert '"inputs"' not in encoded
    assert "private note should not export" not in encoded
    assert "https://example.test/private-source" not in encoded
    assert "demand_momentum" not in encoded
