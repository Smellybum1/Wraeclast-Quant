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


def test_public_intel_includes_recent_runs(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["recent_runs"] == [
        {
            "id": 2,
            "created_at": "2026-05-23T01:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        {
            "id": 1,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
    ]


def test_public_intel_includes_score_trends(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["score_trends"] == [
        {
            "item_name": "Stormglass Catalyst",
            "points": [
                {"run_id": 2, "score": 76.0, "action": "BUY"},
                {"run_id": 1, "score": 50.0, "action": "HOLD / SELL SELECTIVELY"},
            ],
        }
    ]


def test_public_intel_history_respects_limit(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources), limit=1)

    assert payload is not None
    assert len(payload["recent_runs"]) == 1
    assert len(payload["score_trends"]) == 1
    assert len(payload["score_trends"][0]["points"]) == 1
    assert payload["score_trends"][0]["points"][0]["run_id"] == 2
