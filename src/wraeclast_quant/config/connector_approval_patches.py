from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_approval_decisions import connector_approval_helper
from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalPatchResult,
    ConnectorPolicyError,
    ConnectorReview,
)
from wraeclast_quant.config.connector_policy_utils import allowed_use_patch
from wraeclast_quant.config.resources_loader import Resource


def connector_approval_patch(
    review: ConnectorReview,
    resources: list[Resource],
    resources_markdown: str,
    resources_label: str = "RESOURCES.md",
) -> ConnectorApprovalPatchResult:
    approval = connector_approval_helper(review, resources)
    if not approval.suggestion_available:
        return ConnectorApprovalPatchResult(
            review=review,
            resource=approval.resource,
            approval=approval,
            patch_available=False,
            patch_text="",
            reason=approval.reason,
            blockers=approval.blockers,
        )

    assert approval.resource is not None
    try:
        patch_text = allowed_use_patch(
            resources_markdown,
            approval.resource,
            review.access_method,
            resources_label,
        )
    except ConnectorPolicyError as error:
        return ConnectorApprovalPatchResult(
            review=review,
            resource=approval.resource,
            approval=approval,
            patch_available=False,
            patch_text="",
            reason=str(error),
            blockers=[str(error)],
        )

    return ConnectorApprovalPatchResult(
        review=review,
        resource=approval.resource,
        approval=approval,
        patch_available=True,
        patch_text=patch_text,
        reason="Patch preview is available. Manually review and apply it only after approval.",
        blockers=[],
    )


def write_connector_approval_patch(
    review: ConnectorReview,
    resources: list[Resource],
    resources_markdown: str,
    output_path: str | Path,
    resources_label: str = "RESOURCES.md",
) -> Path:
    result = connector_approval_patch(review, resources, resources_markdown, resources_label)
    if not result.patch_available:
        raise ConnectorPolicyError(result.reason)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.patch_text, encoding="utf-8")
    return path
