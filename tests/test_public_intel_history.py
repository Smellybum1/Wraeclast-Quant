from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.reports.public_intel import build_public_intel

from public_intel_helpers import repository_with_runs as _repository_with_runs
from public_intel_helpers import resources as _resources


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
