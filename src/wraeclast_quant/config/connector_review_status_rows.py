from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ALLOWED_ACCESS_METHODS,
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatusRow,
)
from wraeclast_quant.config.connector_policy_utils import (
    boolean_status_row,
    evidence_status_row,
    inverse_boolean_status_row,
    optional_status_row,
    required_when_complete_status_row,
)


def build_connector_review_status_rows(
    review: ConnectorReview,
    result: ConnectorCheckResult,
) -> list[ConnectorReviewStatusRow]:
    resource_status = "ok" if result.resource is not None else "blocked"
    preflight_value = result.preflight.status if result.preflight is not None else "missing"
    preflight_status = (
        "ok"
        if result.preflight is not None and result.preflight.automation_eligible
        else "blocked"
    )

    return [
        ConnectorReviewStatusRow(
            check="Resource match",
            value=result.resource.name if result.resource is not None else review.resource_name,
            status=resource_status,
        ),
        ConnectorReviewStatusRow(
            check="Access method",
            value=review.access_method,
            status="ok" if review.access_method in ALLOWED_ACCESS_METHODS else "blocked",
        ),
        ConnectorReviewStatusRow(
            check="Preflight",
            value=preflight_value,
            status=preflight_status,
        ),
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
            review.source_terms_reviewed and review.robots_or_api_policy_reviewed,
        ),
        required_when_complete_status_row(
            "Allowed data shape",
            review.allowed_data_shape,
            review.source_terms_reviewed and review.robots_or_api_policy_reviewed,
        ),
        optional_status_row("Review notes", review.review_notes),
        inverse_boolean_status_row(
            "Authentication required",
            review.authentication_required,
        ),
        inverse_boolean_status_row("Login required", review.login_required),
        inverse_boolean_status_row("CAPTCHA gated", review.captcha_gated),
        inverse_boolean_status_row("Private data risk", review.private_data_risk),
        ConnectorReviewStatusRow(
            check="Rate limit",
            value=f"{review.rate_limit_per_minute:g}/min",
            status="ok" if review.rate_limit_per_minute > 0 else "blocked",
        ),
        ConnectorReviewStatusRow(
            check="Cache TTL",
            value=f"{review.cache_ttl_seconds}s",
            status="ok" if review.cache_ttl_seconds > 0 else "blocked",
        ),
        boolean_status_row("Dry-run supported", review.dry_run_supported),
        boolean_status_row(
            "Derived-only public export",
            review.public_export_derived_only,
        ),
        ConnectorReviewStatusRow(
            check="Readiness",
            value="ready" if result.ready else "not ready",
            status="ok" if result.ready else "blocked",
        ),
    ]
