from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from wraeclast_quant.storage.models import (
    AnalysisRunRecord,
    ReviewCoverageRecord,
    StoredOpportunityRecord,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

STASH_NINJA_WATCHLIST_SCHEMA_VERSION = "1.0"


def build_stash_ninja_watchlist(
    repository: SnapshotRepository,
    run_id: int | None = None,
    limit: int = 10,
    min_score: float = 55.0,
) -> dict[str, Any] | None:
    run = repository.analysis_run(run_id) if run_id is not None else repository.latest_run()
    if run is None:
        return None

    opportunities = [
        opportunity
        for opportunity in repository.scored_opportunities_for_run(run.id, limit=None)
        if opportunity.opportunity_score >= min_score
    ][:limit]
    coverage = repository.review_coverage_for_run(run.id)
    return _payload(run, opportunities, coverage)


def _payload(
    run: AnalysisRunRecord,
    opportunities: list[StoredOpportunityRecord],
    coverage: ReviewCoverageRecord,
) -> dict[str, Any]:
    return {
        "schema_version": STASH_NINJA_WATCHLIST_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "latest_run": {
            "id": run.id,
            "source_mode": run.source_mode,
            "created_at": run.created_at,
        },
        "review_coverage": {
            "run_id": coverage.run_id,
            "total_recommendations": coverage.total_recommendations,
            "reviewed_recommendations": coverage.reviewed_recommendations,
            "unreviewed_recommendations": coverage.unreviewed_recommendations,
            "reviewed_percent": round(coverage.reviewed_percent, 1),
        },
        "items": [_item_payload(opportunity) for opportunity in opportunities],
        "safety": {
            "derived_only": True,
            "manual_application_required": True,
            "no_exile_ui_writes": True,
            "no_game_client_interaction": True,
            "no_live_http": True,
            "no_raw_signals": True,
        },
    }


def _item_payload(opportunity: StoredOpportunityRecord) -> dict[str, Any]:
    return {
        "item_name": opportunity.item_name,
        "opportunity_score": round(opportunity.opportunity_score, 2),
        "action": opportunity.action,
        "suggested_stash_ninja_treatment": _suggested_treatment(opportunity),
    }


def _suggested_treatment(opportunity: StoredOpportunityRecord) -> str:
    if opportunity.action == "BUY" or opportunity.opportunity_score >= 75.0:
        return "bookmark-candidate"
    if opportunity.action == "WATCH" or opportunity.opportunity_score >= 55.0:
        return "watch"
    return "manual-review"


__all__ = [
    "STASH_NINJA_WATCHLIST_SCHEMA_VERSION",
    "build_stash_ninja_watchlist",
]
