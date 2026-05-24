from __future__ import annotations

from typing import Any

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatus,
)
from wraeclast_quant.config.connector_review_report_audit_sections import (
    checklist_section,
    evidence_section,
    readiness_section,
    resource_section,
)
from wraeclast_quant.config.connector_review_report_plan_sections import (
    blockers_section,
    fetch_plan_section,
    limits_section,
    next_step_section,
    safety_section,
)


def connector_review_report_markdown(
    review: ConnectorReview,
    check: ConnectorCheckResult,
    status: ConnectorReviewStatus,
    approval: ConnectorApprovalHelperResult,
    fetch_plan: Any,
) -> str:
    lines = [
        f"# Connector Review Report: {review.resource_name}",
        "",
        "This report is a local audit handoff. It does not approve automation, fetch data, edit RESOURCES.md, publish artifacts, or implement a connector.",
        "",
        *resource_section(review, check),
        *readiness_section(check, approval),
        *checklist_section(status),
        *evidence_section(review),
        *safety_section(review),
        *limits_section(review),
        *blockers_section(check),
        *fetch_plan_section(fetch_plan),
        *next_step_section(check, approval),
    ]
    return "\n".join(lines)
