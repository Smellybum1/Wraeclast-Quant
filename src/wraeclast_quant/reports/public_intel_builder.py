from __future__ import annotations

from typing import Any

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel_build_context import load_public_intel_build_context
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
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_public_intel(
    repository: SnapshotRepository,
    resources: list[Resource],
    assessments: list[ComplianceAssessment],
    limit: int = 10,
    generated_at: str | None = None,
    alert_settings: AlertRuleSettings | None = None,
) -> dict[str, Any] | None:
    context = load_public_intel_build_context(
        repository,
        limit=limit,
        alert_settings=alert_settings,
    )
    if context is None:
        return None

    return {
        "schema_version": PUBLIC_INTEL_SCHEMA_VERSION,
        "generated_at": generated_at or utc_now(),
        "latest_run": run_payload(context.latest),
        "recent_runs": [run_payload(run) for run in context.recent_runs],
        "top_opportunities": [
            opportunity_payload(opportunity) for opportunity in context.latest_opportunities
        ],
        "score_trends": score_trends_payload(
            repository=repository,
            recent_runs=context.recent_runs,
            latest_opportunities=context.latest_opportunities,
        ),
        "snapshot_changes": snapshot_changes_payload(context.comparison, limit=limit),
        "alerts": [alert_payload(alert) for alert in context.alerts[:limit]],
        "outcome_summary": repository.outcome_summary(),
        "review_coverage": review_coverage_payload(repository, context.latest),
        "compliance_summary": compliance_summary(assessments, total_resources=len(resources)),
    }
