from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorReview,
    ConnectorReviewStatusRow,
)
from wraeclast_quant.config.connector_policy_utils import (
    boolean_status_row,
    evidence_status_row,
    optional_status_row,
    required_when_complete_status_row,
)


def evidence_status_rows(review: ConnectorReview) -> list[ConnectorReviewStatusRow]:
    evidence_complete = review.source_terms_reviewed and review.robots_or_api_policy_reviewed
    return [
        boolean_status_row("Source terms reviewed", review.source_terms_reviewed),
        evidence_status_row(
            "Source terms URL",
            review.source_terms_url,
            review.source_terms_reviewed,
        ),
        boolean_status_row(
            "Robots/API policy reviewed",
            review.robots_or_api_policy_reviewed,
        ),
        evidence_status_row(
            "Robots/API policy URL",
            review.robots_or_api_policy_url,
            review.robots_or_api_policy_reviewed,
        ),
        required_when_complete_status_row(
            "Reviewed at",
            review.reviewed_at,
            evidence_complete,
        ),
        required_when_complete_status_row(
            "Allowed data shape",
            review.allowed_data_shape,
            evidence_complete,
        ),
        optional_status_row("Review notes", review.review_notes),
    ]
