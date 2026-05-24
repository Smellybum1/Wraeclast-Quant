from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatus,
)
from wraeclast_quant.config.connector_policy_utils import (
    markdown_cell,
    markdown_value,
    report_row_value,
    safe_url,
    yes_no,
)


def resource_section(review: ConnectorReview, check: ConnectorCheckResult) -> list[str]:
    return [
        "## Resource",
        "",
        f"- Resource name: `{review.resource_name}`",
        f"- Resource id: `{check.resource.id if check.resource is not None else ''}`",
        f"- Resource type: `{check.resource.type if check.resource is not None else 'missing'}`",
        f"- Current allowed_use: `{check.resource.allowed_use if check.resource is not None else 'missing'}`",
        f"- Requested access method: `{review.access_method}`",
        "",
    ]


def readiness_section(
    check: ConnectorCheckResult,
    approval: ConnectorApprovalHelperResult,
) -> list[str]:
    return [
        "## Preflight And Readiness",
        "",
        f"- Preflight status: `{check.preflight.status if check.preflight is not None else 'missing'}`",
        f"- Connector-check readiness: `{'ready' if check.ready else 'not ready'}`",
        f"- Approval suggestion: `{approval.approval_suggestion if approval.suggestion_available else 'None'}`",
        f"- Approval helper reason: {markdown_value(approval.reason)}",
        "",
    ]


def checklist_section(status: ConnectorReviewStatus) -> list[str]:
    lines = [
        "## Review Checklist",
        "",
        "| Check | Value | Status |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {markdown_cell(row.check)} | {markdown_cell(report_row_value(row.check, row.value))} | {markdown_cell(row.status)} |"
        for row in status.rows
    )
    return lines


def evidence_section(review: ConnectorReview) -> list[str]:
    return [
        "",
        "## Evidence",
        "",
        f"- Source terms reviewed: `{yes_no(review.source_terms_reviewed)}`",
        f"- Source terms URL: `{safe_url(review.source_terms_url)}`",
        f"- Robots/API policy reviewed: `{yes_no(review.robots_or_api_policy_reviewed)}`",
        f"- Robots/API policy URL: `{safe_url(review.robots_or_api_policy_url)}`",
        f"- Reviewed at: `{review.reviewed_at}`",
        f"- Allowed data shape: {markdown_value(review.allowed_data_shape)}",
        f"- Review notes recorded: `{yes_no(bool(review.review_notes.strip()))}`",
        "",
    ]
