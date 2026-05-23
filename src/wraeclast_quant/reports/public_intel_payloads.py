from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.intelligence.alerts import AlertCandidate
from wraeclast_quant.intelligence.snapshot_deltas import OpportunityDelta, SnapshotComparison
from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def run_payload(run: AnalysisRunRecord) -> dict[str, Any]:
    return {
        "id": run.id,
        "created_at": run.created_at,
        "source_mode": run.source_mode,
        "item_count": run.item_count,
    }


def opportunity_payload(opportunity: StoredOpportunityRecord) -> dict[str, Any]:
    return {
        "item_name": opportunity.item_name,
        "opportunity_score": opportunity.opportunity_score,
        "action": opportunity.action,
    }


def review_coverage_payload(
    repository: SnapshotRepository,
    latest: AnalysisRunRecord,
) -> dict[str, Any]:
    coverage = repository.review_coverage_for_run(latest.id)
    return {
        "run_id": coverage.run_id,
        "total_recommendations": coverage.total_recommendations,
        "reviewed_recommendations": coverage.reviewed_recommendations,
        "unreviewed_recommendations": coverage.unreviewed_recommendations,
        "reviewed_percent": round(coverage.reviewed_percent, 1),
    }


def score_trends_payload(
    repository: SnapshotRepository,
    recent_runs: list[AnalysisRunRecord],
    latest_opportunities: list[StoredOpportunityRecord],
) -> list[dict[str, Any]]:
    opportunities_by_run = {
        run.id: {
            opportunity.item_name: opportunity
            for opportunity in repository.scored_opportunities_for_run(run.id)
        }
        for run in recent_runs
    }
    trends = []
    for latest_opportunity in latest_opportunities:
        points = []
        for run in recent_runs:
            opportunity = opportunities_by_run[run.id].get(latest_opportunity.item_name)
            if opportunity is None:
                continue
            points.append(
                {
                    "run_id": run.id,
                    "score": opportunity.opportunity_score,
                    "action": opportunity.action,
                }
            )
        trends.append({"item_name": latest_opportunity.item_name, "points": points})
    return trends


def snapshot_changes_payload(
    comparison: SnapshotComparison | None,
    limit: int,
) -> dict[str, Any]:
    if comparison is None:
        return {
            "previous_run_id": None,
            "latest_run_id": None,
            "top_movers": [],
            "status_changes": [],
        }
    return {
        "previous_run_id": comparison.previous_run_id,
        "latest_run_id": comparison.latest_run_id,
        "top_movers": [delta_payload(delta) for delta in comparison.top_movers[:limit]],
        "status_changes": [delta_payload(delta) for delta in comparison.status_changes[:limit]],
    }


def delta_payload(delta: OpportunityDelta) -> dict[str, Any]:
    return {
        "item_name": delta.item_name,
        "status": delta.status,
        "previous_score": delta.previous_score,
        "latest_score": delta.latest_score,
        "score_delta": delta.score_delta,
        "previous_action": delta.previous_action,
        "latest_action": delta.latest_action,
    }


def alert_payload(alert: AlertCandidate) -> dict[str, Any]:
    return {
        "severity": alert.severity,
        "item_name": alert.item_name,
        "reason": alert.reason,
        "previous_score": alert.previous_score,
        "latest_score": alert.latest_score,
        "score_delta": alert.score_delta,
        "previous_action": alert.previous_action,
        "latest_action": alert.latest_action,
    }


def compliance_summary(
    assessments: list[ComplianceAssessment],
    total_resources: int,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    automation_eligible_count = 0
    for assessment in assessments:
        status_counts[assessment.status] = status_counts.get(assessment.status, 0) + 1
        if assessment.automation_eligible:
            automation_eligible_count += 1
    return {
        "total_resources": total_resources,
        "status_counts": dict(sorted(status_counts.items())),
        "automation_eligible_count": automation_eligible_count,
    }
