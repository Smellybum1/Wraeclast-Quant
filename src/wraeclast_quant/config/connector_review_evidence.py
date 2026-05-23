from __future__ import annotations

import re

from wraeclast_quant.config.connector_policy_models import (
    ConnectorPolicyError,
    ConnectorReview,
)


def update_connector_review_evidence(
    review: ConnectorReview,
    source_terms_url: str | None = None,
    robots_or_api_policy_url: str | None = None,
    reviewed_at: str | None = None,
    allowed_data_shape: str | None = None,
    review_notes: str | None = None,
    rate_limit_per_minute: float | None = None,
    cache_ttl_seconds: int | None = None,
    authentication_required: bool | None = None,
    login_required: bool | None = None,
    captcha_gated: bool | None = None,
    private_data_risk: bool | None = None,
) -> ConnectorReview:
    data = review.model_dump()
    if source_terms_url is not None:
        data["source_terms_url"] = source_terms_url
        data["source_terms_reviewed"] = True
    if robots_or_api_policy_url is not None:
        data["robots_or_api_policy_url"] = robots_or_api_policy_url
        data["robots_or_api_policy_reviewed"] = True
    if reviewed_at is not None:
        if reviewed_at and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at):
            raise ConnectorPolicyError("reviewed_at must use YYYY-MM-DD format.")
        data["reviewed_at"] = reviewed_at
    if allowed_data_shape is not None:
        data["allowed_data_shape"] = allowed_data_shape
    if review_notes is not None:
        data["review_notes"] = review_notes
    if rate_limit_per_minute is not None:
        if rate_limit_per_minute <= 0:
            raise ConnectorPolicyError("rate_limit_per_minute must be positive.")
        data["rate_limit_per_minute"] = rate_limit_per_minute
    if cache_ttl_seconds is not None:
        if cache_ttl_seconds <= 0:
            raise ConnectorPolicyError("cache_ttl_seconds must be positive.")
        data["cache_ttl_seconds"] = cache_ttl_seconds
    if authentication_required is not None:
        data["authentication_required"] = authentication_required
    if login_required is not None:
        data["login_required"] = login_required
    if captcha_gated is not None:
        data["captcha_gated"] = captcha_gated
    if private_data_risk is not None:
        data["private_data_risk"] = private_data_risk

    return ConnectorReview.model_validate(data)
