from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


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
    authentication_approved: bool = False
    credential_storage_reviewed: bool = False
    login_required: bool = False
    captcha_gated: bool = False
    private_data_risk: bool = False
    rate_limit_per_minute: float
    cache_ttl_seconds: int
    dry_run_supported: bool
    public_export_derived_only: bool


class ConnectorReviewPrepResult(BaseModel):
    review: ConnectorReview
    review_path: Path
    checklist_path: Path
    next_commands: list[str]


__all__ = ["ConnectorReview", "ConnectorReviewPrepResult"]
