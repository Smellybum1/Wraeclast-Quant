import json
from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.reports.public_intel import build_public_intel

from public_intel_helpers import repository_with_runs as _repository_with_runs
from public_intel_helpers import resources as _resources


def test_public_intel_includes_outcome_summary_without_notes(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    repository.save_recommendation_outcome(
        run_id=2,
        item_name="Stormglass Catalyst",
        outcome="positive",
        notes="private outcome note should not export",
    )
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["outcome_summary"] == {
        "negative": 0,
        "neutral": 0,
        "positive": 1,
    }
    encoded = json.dumps(payload)
    assert "private outcome note should not export" not in encoded


def test_public_intel_includes_latest_run_review_coverage_without_notes(
    tmp_path: Path,
) -> None:
    repository = _repository_with_runs(tmp_path)
    repository.save_recommendation_outcome(
        run_id=2,
        item_name="Stormglass Catalyst",
        outcome="positive",
        notes="private review coverage note should not export",
    )
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["review_coverage"] == {
        "run_id": 2,
        "total_recommendations": 1,
        "reviewed_recommendations": 1,
        "unreviewed_recommendations": 0,
        "reviewed_percent": 100.0,
    }
    encoded = json.dumps(payload)
    assert "private review coverage note should not export" not in encoded
