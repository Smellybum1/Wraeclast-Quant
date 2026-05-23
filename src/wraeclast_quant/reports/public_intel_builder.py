from __future__ import annotations

from typing import Any

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.intelligence.alerts import AlertRuleSettings, generate_alerts
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison, compare_opportunities
from wraeclast_quant.reports.public_intel_constants import PUBLIC_INTEL_SCHEMA_VERSION
from wraeclast_quant.reports.public_intel_payloads import (
    alert_payload,
    compliance_summary,
    opportunity_payload,
    review_coverage_payload,
    run_payload,
    score_trends_payload,
    snapshot_changes_payload,
    utc_now,
)
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_public_intel(
    repository: SnapshotRepository,
    resources: list[Resource],
    assessments: list[ComplianceAssessment],
    limit: int = 10,
    generated_at: str | None = None,
    alert_settings: AlertRuleSettings | None = None,
) -> dict[str, Any] | None:
    latest = repository.latest_run()
    if latest is None:
        return None

    latest_opportunities = repository.scored_opportunities_for_run(latest.id, limit=limit)
    recent_runs = repository.list_recent_runs(limit=limit)
    previous = repository.previous_run_before(latest.id)
    comparison = _build_comparison(repository, previous, latest)
    alerts = generate_alerts(comparison, settings=alert_settings) if comparison is not None else []

    return {
        "schema_version": PUBLIC_INTEL_SCHEMA_VERSION,
        "generated_at": generated_at or utc_now(),
        "latest_run": run_payload(latest),
        "recent_runs": [run_payload(run) for run in recent_runs],
        "top_opportunities": [
            opportunity_payload(opportunity) for opportunity in latest_opportunities
        ],
        "score_trends": score_trends_payload(
            repository=repository,
            recent_runs=recent_runs,
            latest_opportunities=latest_opportunities,
        ),
        "snapshot_changes": snapshot_changes_payload(comparison, limit=limit),
        "alerts": [alert_payload(alert) for alert in alerts[:limit]],
        "outcome_summary": repository.outcome_summary(),
        "review_coverage": review_coverage_payload(repository, latest),
        "compliance_summary": compliance_summary(assessments, total_resources=len(resources)),
    }


def _build_comparison(
    repository: SnapshotRepository,
    previous: AnalysisRunRecord | None,
    latest: AnalysisRunRecord,
) -> SnapshotComparison | None:
    if previous is None:
        return None
    return compare_opportunities(
        previous=repository.scored_opportunities_for_run(previous.id),
        latest=repository.scored_opportunities_for_run(latest.id),
        previous_run_id=previous.id,
        latest_run_id=latest.id,
    )
