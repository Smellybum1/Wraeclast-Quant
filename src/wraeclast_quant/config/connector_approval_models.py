from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.connector_check_models import ConnectorCheckResult
from wraeclast_quant.config.connector_review_models import ConnectorReview
from wraeclast_quant.config.preflight import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource


class ConnectorApprovalHelperResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    preflight: PreflightAssessment | None
    check_result: ConnectorCheckResult
    evidence_ready: bool
    connector_check_ready: bool
    suggestion_available: bool
    approval_suggestion: str
    reason: str
    blockers: list[str]


class ConnectorApprovalPatchResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    approval: ConnectorApprovalHelperResult
    patch_available: bool
    patch_text: str
    reason: str
    blockers: list[str]


__all__ = ["ConnectorApprovalHelperResult", "ConnectorApprovalPatchResult"]
