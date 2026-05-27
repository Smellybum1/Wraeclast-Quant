from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wraeclast_quant.storage.models import (
    AnalysisRunRecord,
    ReviewCoverageRecord,
    StoredOpportunityRecord,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

DEFAULT_STASH_NINJA_WATCHLIST_PATH = Path("data/processed/exile_ui_stash_ninja_watchlist.json")
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


def write_stash_ninja_watchlist(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_stash_ninja_watchlist_markdown(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_stash_ninja_watchlist_markdown(payload), encoding="utf-8")
    return output_path


def render_stash_ninja_watchlist_markdown(payload: dict[str, Any]) -> str:
    run = payload["latest_run"]
    coverage = payload["review_coverage"]
    lines = [
        "# Exile-UI Stash-Ninja Companion Watchlist",
        "",
        "Derived-only local handoff for manually configuring or checking Stash-Ninja. "
        "This file does not write Exile-UI settings, automate the overlay, or interact with the game client.",
        "",
        f"- Run: #{run['id']} ({run['source_mode']})",
        f"- Created at: {run['created_at']}",
        (
            "- Review coverage: "
            f"{coverage['reviewed_recommendations']}/{coverage['total_recommendations']} reviewed "
            f"({coverage['reviewed_percent']:.1f}%)"
        ),
        (
            "- Next manual review: "
            f"wq review-queue --run-id {run['id']} "
            "--output-path data/processed/review_queue.md"
        ),
        "",
        "| Item | Score | Action | Suggested manual treatment |",
        "| --- | ---: | --- | --- |",
    ]
    for item in payload["items"]:
        lines.append(
            "| "
            f"{item['item_name']} | "
            f"{item['opportunity_score']:.2f} | "
            f"{item['action']} | "
            f"{item['suggested_stash_ninja_treatment']} |"
        )
    if not payload["items"]:
        lines.append("| _No items met the score threshold._ |  |  |  |")
    lines.extend(
        [
            "",
            "Manual application required: inspect these recommendations yourself before changing any overlay settings.",
            "",
        ]
    )
    return "\n".join(lines)


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
    "DEFAULT_STASH_NINJA_WATCHLIST_PATH",
    "STASH_NINJA_WATCHLIST_SCHEMA_VERSION",
    "build_stash_ninja_watchlist",
    "render_stash_ninja_watchlist_markdown",
    "write_stash_ninja_watchlist",
    "write_stash_ninja_watchlist_markdown",
]
