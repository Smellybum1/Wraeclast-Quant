from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorReview,
    ConnectorReviewStatusRow,
)
from wraeclast_quant.config.connector_policy_utils import (
    boolean_status_row,
    inverse_boolean_status_row,
)


def safety_status_rows(review: ConnectorReview) -> list[ConnectorReviewStatusRow]:
    return [
        inverse_boolean_status_row(
            "Authentication required",
            review.authentication_required,
        ),
        inverse_boolean_status_row("Login required", review.login_required),
        inverse_boolean_status_row("CAPTCHA gated", review.captcha_gated),
        inverse_boolean_status_row("Private data risk", review.private_data_risk),
    ]


def execution_status_rows(review: ConnectorReview) -> list[ConnectorReviewStatusRow]:
    return [
        boolean_status_row("Dry-run supported", review.dry_run_supported),
        boolean_status_row(
            "Derived-only public export",
            review.public_export_derived_only,
        ),
    ]
