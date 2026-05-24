from __future__ import annotations

from typing import Any

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatus,
)
from wraeclast_quant.config.connector_policy_utils import (
    markdown_cell,
    markdown_value,
    next_step,
    report_row_value,
    safe_url,
    yes_no,
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
        *_resource_section(review, check),
        *_readiness_section(check, approval),
        *_checklist_section(status),
        *_evidence_section(review),
        *_safety_section(review),
        *_limits_section(review),
        *_blockers_section(check),
        *_fetch_plan_section(fetch_plan),
        *_next_step_section(check, approval),
    ]
    return "\n".join(lines)


def _resource_section(review: ConnectorReview, check: ConnectorCheckResult) -> list[str]:
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


def _readiness_section(
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


def _checklist_section(status: ConnectorReviewStatus) -> list[str]:
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


def _evidence_section(review: ConnectorReview) -> list[str]:
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


def _safety_section(review: ConnectorReview) -> list[str]:
    return [
        "## Safety Flags",
        "",
        f"- Authentication required: `{yes_no(review.authentication_required)}`",
        f"- Login required: `{yes_no(review.login_required)}`",
        f"- CAPTCHA gated: `{yes_no(review.captcha_gated)}`",
        f"- Private data risk: `{yes_no(review.private_data_risk)}`",
        f"- Dry-run supported: `{yes_no(review.dry_run_supported)}`",
        f"- Derived-only public export: `{yes_no(review.public_export_derived_only)}`",
        "",
    ]


def _limits_section(review: ConnectorReview) -> list[str]:
    return [
        "## Limits",
        "",
        f"- Rate limit: `{review.rate_limit_per_minute:g}/min`",
        f"- Cache TTL: `{review.cache_ttl_seconds}s`",
        "",
    ]


def _blockers_section(check: ConnectorCheckResult) -> list[str]:
    lines = ["## Blockers", ""]
    if check.blockers:
        lines.extend(f"- {markdown_value(blocker)}" for blocker in check.blockers)
    else:
        lines.append("- None")
    return lines


def _fetch_plan_section(fetch_plan: Any) -> list[str]:
    lines = ["", "## Fetch Plan Summary", ""]
    if fetch_plan is None:
        lines.append("- No fetch plan is available until connector-check passes.")
    else:
        lines.extend(
            [
                f"- Cache path: `{fetch_plan.cache_path}`",
                f"- Cache TTL: `{fetch_plan.cache_ttl_seconds}s`",
                f"- Rate limit: `{fetch_plan.rate_limit_per_minute:g}/min`",
                f"- Minimum request interval: `{fetch_plan.min_seconds_between_requests:.2f}s`",
                f"- Dry-run required: `{yes_no(fetch_plan.dry_run_required)}`",
                f"- Derived-only public export: `{yes_no(fetch_plan.public_export_derived_only)}`",
            ]
        )
    return lines


def _next_step_section(
    check: ConnectorCheckResult,
    approval: ConnectorApprovalHelperResult,
) -> list[str]:
    return [
        "",
        "## Next Step",
        "",
        next_step(check, approval),
        "",
    ]
