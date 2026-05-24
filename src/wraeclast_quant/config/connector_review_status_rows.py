from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatusRow,
)
from wraeclast_quant.config.connector_review_status_core_rows import core_status_rows
from wraeclast_quant.config.connector_review_status_evidence_rows import evidence_status_rows
from wraeclast_quant.config.connector_review_status_limit_rows import limit_status_rows
from wraeclast_quant.config.connector_review_status_readiness_rows import readiness_status_row
from wraeclast_quant.config.connector_review_status_safety_rows import (
    execution_status_rows,
    safety_status_rows,
)


def build_connector_review_status_rows(
    review: ConnectorReview,
    result: ConnectorCheckResult,
) -> list[ConnectorReviewStatusRow]:
    return [
        *core_status_rows(review, result),
        *evidence_status_rows(review),
        *safety_status_rows(review),
        *limit_status_rows(review),
        *execution_status_rows(review),
        readiness_status_row(result),
    ]


__all__ = ["build_connector_review_status_rows"]
