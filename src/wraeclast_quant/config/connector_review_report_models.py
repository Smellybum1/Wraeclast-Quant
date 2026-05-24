from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.connector_approval_models import ConnectorApprovalHelperResult
from wraeclast_quant.config.connector_check_models import ConnectorCheckResult
from wraeclast_quant.config.connector_review_models import ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


class ConnectorReviewReportResult(BaseModel):
    review: ConnectorReview
    resource: Resource | None
    check_result: ConnectorCheckResult
    approval: ConnectorApprovalHelperResult
    markdown: str


__all__ = ["ConnectorReviewReportResult"]
