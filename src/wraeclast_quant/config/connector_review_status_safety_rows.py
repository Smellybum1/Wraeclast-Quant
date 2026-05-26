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
    auth_status = (
        boolean_status_row("Authentication approved", review.authentication_approved)
        if review.authentication_required
        else boolean_status_row("Authentication approved", True)
    )
    credential_status = (
        boolean_status_row(
            "Credential storage reviewed",
            review.credential_storage_reviewed,
        )
        if review.authentication_required
        else boolean_status_row("Credential storage reviewed", True)
    )
    return [
        _authentication_required_row(review),
        auth_status,
        credential_status,
        inverse_boolean_status_row("Login required", review.login_required),
        inverse_boolean_status_row("CAPTCHA gated", review.captcha_gated),
        inverse_boolean_status_row("Private data risk", review.private_data_risk),
    ]


def _authentication_required_row(review: ConnectorReview) -> ConnectorReviewStatusRow:
    if not review.authentication_required:
        return ConnectorReviewStatusRow(
            check="Authentication required",
            value="no",
            status="ok",
        )
    status = "ok" if review.authentication_approved and review.credential_storage_reviewed else "blocked"
    return ConnectorReviewStatusRow(
        check="Authentication required",
        value="yes",
        status=status,
    )


def execution_status_rows(review: ConnectorReview) -> list[ConnectorReviewStatusRow]:
    return [
        boolean_status_row("Dry-run supported", review.dry_run_supported),
        boolean_status_row(
            "Derived-only public export",
            review.public_export_derived_only,
        ),
    ]
