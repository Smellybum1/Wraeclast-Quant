from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_policy_models import (
    AUTOMATION_ACCESS_METHODS,
    ConnectorApprovalHelperResult,
    ConnectorApprovalPatchResult,
    ConnectorPolicyError,
    ConnectorReview,
)
from wraeclast_quant.config.connector_policy_utils import allowed_use_patch
from wraeclast_quant.config.connector_review_checks import check_connector_review
from wraeclast_quant.config.resources_loader import Resource


def connector_approval_helper(
    review: ConnectorReview,
    resources: list[Resource],
) -> ConnectorApprovalHelperResult:
    check = check_connector_review(review, resources)
    non_preflight_blockers = [
        blocker
        for blocker in check.blockers
        if not blocker.startswith("Resource is not automation-eligible:")
    ]
    evidence_ready = not non_preflight_blockers

    suggestion_available = False
    approval_suggestion = "None"
    reason = "Resolve review blockers before an approval suggestion is available."

    if check.resource is None:
        reason = "No matching resource found in RESOURCES.md."
    elif check.resource.type.strip().lower() == "discord":
        reason = "Discord resources require a separate approved-bot/API compliance gate."
    elif review.access_method not in AUTOMATION_ACCESS_METHODS:
        reason = "Manual-export reviews do not require an automation allowed_use change."
    elif check.preflight is not None and check.preflight.automation_eligible:
        reason = "No approval change needed; resource is already automation-eligible."
    elif check.resource.allowed_use.strip().lower() in {"blocked", "no-automation"}:
        reason = "No approval suggestion is available for blocked or no-automation sources."
    elif not check.resource.url.strip():
        reason = "Add a source URL before considering an automation approval change."
    elif evidence_ready:
        suggestion_available = True
        approval_suggestion = f"allowed_use: {review.access_method}"
        reason = "After human approval, manually update RESOURCES.md with the suggested allowed_use."

    return ConnectorApprovalHelperResult(
        review=review,
        resource=check.resource,
        preflight=check.preflight,
        check_result=check,
        evidence_ready=evidence_ready,
        connector_check_ready=check.ready,
        suggestion_available=suggestion_available,
        approval_suggestion=approval_suggestion,
        reason=reason,
        blockers=check.blockers,
    )


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
