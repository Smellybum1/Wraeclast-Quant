from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorReview,
    ConnectorReviewStatus,
)
from wraeclast_quant.config.connector_review_readiness import check_connector_review
from wraeclast_quant.config.connector_review_status_rows import (
    build_connector_review_status_rows,
)
from wraeclast_quant.config.resources_loader import Resource


def connector_review_status(
    review: ConnectorReview,
    resources: list[Resource],
) -> ConnectorReviewStatus:
    result = check_connector_review(review, resources)
    rows = build_connector_review_status_rows(review, result)
    return ConnectorReviewStatus(check_result=result, rows=rows)
