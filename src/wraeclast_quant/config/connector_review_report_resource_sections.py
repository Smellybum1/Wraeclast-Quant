from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
    ConnectorReview,
)
from wraeclast_quant.config.connector_policy_utils import markdown_value


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


__all__ = ["readiness_section", "resource_section"]
