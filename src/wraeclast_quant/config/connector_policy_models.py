from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from wraeclast_quant.config.connector_policy_constants import (
    ALLOWED_ACCESS_METHODS,
    AUTOMATION_ACCESS_METHODS,
)
from wraeclast_quant.config.connector_policy_errors import ConnectorPolicyError
from wraeclast_quant.config.preflight import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource


class ConnectorReview(BaseModel):
    resource_name: str
    access_method: str
    source_terms_reviewed: bool
    robots_or_api_policy_reviewed: bool
    source_terms_url: str = ""
    robots_or_api_policy_url: str = ""
    reviewed_at: str = ""
    review_notes: str = ""
    allowed_data_shape: str = ""
    authentication_required: bool = False
    login_required: bool = False
    captcha_gated: bool = False
    private_data_risk: bool = False
    rate_limit_per_minute: float
    cache_ttl_seconds: int
    dry_run_supported: bool
    public_export_derived_only: bool


class ConnectorCheckResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    preflight: PreflightAssessment | None
    ready: bool
    blockers: list[str]


class ConnectorReviewStatusRow(BaseModel):
    check: str
    value: str
    status: str


class ConnectorReviewStatus(BaseModel):
    check_result: ConnectorCheckResult
    rows: list[ConnectorReviewStatusRow]


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


class ConnectorReviewPrepResult(BaseModel):
    review: ConnectorReview
    review_path: Path
    checklist_path: Path
    next_commands: list[str]


class ConnectorReviewReportResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    check_result: ConnectorCheckResult
    approval: ConnectorApprovalHelperResult
    markdown: str


class ConnectorApprovalPatchResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    approval: ConnectorApprovalHelperResult
    patch_available: bool
    patch_text: str
    reason: str
    blockers: list[str]


__all__ = [
    "ALLOWED_ACCESS_METHODS",
    "AUTOMATION_ACCESS_METHODS",
    "ConnectorApprovalHelperResult",
    "ConnectorApprovalPatchResult",
    "ConnectorCheckResult",
    "ConnectorPolicyError",
    "ConnectorReview",
    "ConnectorReviewPrepResult",
    "ConnectorReviewReportResult",
    "ConnectorReviewStatus",
    "ConnectorReviewStatusRow",
]
