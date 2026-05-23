import json
from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.scoring import OpportunityInputs, ScoredOpportunity
from wraeclast_quant.reports.public_intel import (
    PUBLIC_INTEL_SCHEMA_VERSION,
    build_public_intel,
    write_public_intel,
)
from wraeclast_quant.storage.repositories import SnapshotRepository


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


def test_public_intel_includes_latest_run_and_top_opportunities(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources), limit=1)

    assert payload is not None
    assert payload["latest_run"]["source_mode"] == "sample-data"
    assert payload["top_opportunities"] == [
        {
            "item_name": "Stormglass Catalyst",
            "opportunity_score": 76.0,
            "action": "BUY",
        }
    ]


def test_public_intel_includes_deltas_and_alerts(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["snapshot_changes"]["previous_run_id"] == 1
    assert payload["snapshot_changes"]["latest_run_id"] == 2
    assert payload["snapshot_changes"]["top_movers"][0]["item_name"] == "Stormglass Catalyst"
    assert payload["alerts"][0]["reason"] == "Score crossed into BUY"


def test_public_intel_uses_tuned_alert_settings(tmp_path: Path) -> None:
    repository = _repository_with_delta_only_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(
        repository,
        resources,
        assess_resources(resources),
        alert_settings=AlertRuleSettings(big_positive_delta=20.0),
    )

    assert payload is not None
    assert payload["alerts"] == []


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


def test_public_intel_includes_latest_run_review_coverage_without_notes(tmp_path: Path) -> None:
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


def test_public_intel_excludes_raw_inputs_and_resource_notes(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    encoded = json.dumps(payload)
    assert '"inputs"' not in encoded
    assert "private note should not export" not in encoded
    assert "https://example.test/private-source" not in encoded
    assert "demand_momentum" not in encoded


def test_public_intel_returns_none_without_snapshots(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is None


def _repository_with_runs(tmp_path: Path) -> SnapshotRepository:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    first = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(
        first.id,
        [_opportunity("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY")],
    )
    second = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T01:00:00+00:00",
    )
    repository.save_scored_opportunities(
        second.id,
        [_opportunity("Stormglass Catalyst", 76.0, "BUY")],
    )
    return repository


def _repository_with_delta_only_runs(tmp_path: Path) -> SnapshotRepository:
    repository = SnapshotRepository(tmp_path / "delta_snapshots.db")
    first = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(first.id, [_opportunity("Small Mover", 20.0, "AVOID")])
    second = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T01:00:00+00:00",
    )
    repository.save_scored_opportunities(second.id, [_opportunity("Small Mover", 30.0, "AVOID")])
    return repository


def _opportunity(name: str, score: float, action: str) -> ScoredOpportunity:
    return ScoredOpportunity(
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs=OpportunityInputs(
            demand_momentum=88,
            build_dependency_score=82,
            price_discount_score=76,
            liquidity_score=70,
            historical_spike_score=68,
            patch_relevance_score=74,
            manipulation_risk=18,
            stale_data_penalty=8,
        ),
    )


def _resources() -> list[Resource]:
    return [
        Resource(
            name="Approved API",
            type="official_docs",
            allowed_use="api",
            url="https://example.test/private-source",
            notes="private note should not export",
        ),
        Resource(name="Manual Source", allowed_use="manual-review"),
        Resource(name="Conditional Source", allowed_use="manual-or-api-if-available"),
    ]
