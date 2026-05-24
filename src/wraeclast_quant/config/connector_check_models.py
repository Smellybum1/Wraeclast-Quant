from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.preflight import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.config.connector_review_models import ConnectorReview


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


__all__ = [
    "ConnectorCheckResult",
    "ConnectorReviewStatus",
    "ConnectorReviewStatusRow",
]
