from pathlib import Path

from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.intelligence.scoring import OpportunityInputs, ScoredOpportunity
from wraeclast_quant.storage.repositories import SnapshotRepository


def repository_with_runs(tmp_path: Path) -> SnapshotRepository:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    first = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(
        first.id,
        [opportunity("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY")],
    )
    second = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T01:00:00+00:00",
    )
    repository.save_scored_opportunities(
        second.id,
        [opportunity("Stormglass Catalyst", 76.0, "BUY")],
    )
    return repository


def repository_with_delta_only_runs(tmp_path: Path) -> SnapshotRepository:
    repository = SnapshotRepository(tmp_path / "delta_snapshots.db")
    first = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(first.id, [opportunity("Small Mover", 20.0, "AVOID")])
    second = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=1,
        created_at="2026-05-23T01:00:00+00:00",
    )
    repository.save_scored_opportunities(second.id, [opportunity("Small Mover", 30.0, "AVOID")])
    return repository


def opportunity(name: str, score: float, action: str) -> ScoredOpportunity:
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


def resources() -> list[Resource]:
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
