from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    ConnectorReview,
    load_connector_review,
    update_connector_review_evidence,
    write_connector_review_draft,
)


@dataclass(frozen=True)
class ConnectorReviewEvidenceUpdate:
    review: ConnectorReview


def update_review_evidence_file(
    *,
    review_path: Path,
    source_terms_url: str | None,
    robots_or_api_policy_url: str | None,
    reviewed_at: str | None,
    allowed_data_shape: str | None,
    review_notes: str | None,
    rate_limit_per_minute: float | None,
    cache_ttl_seconds: int | None,
    authentication_required: bool | None,
    authentication_approved: bool | None,
    credential_storage_reviewed: bool | None,
    login_required: bool | None,
    captcha_gated: bool | None,
    private_data_risk: bool | None,
) -> ConnectorReviewEvidenceUpdate:
    try:
        review = load_connector_review(review_path)
        updated = update_connector_review_evidence(
            review,
            source_terms_url=source_terms_url,
            robots_or_api_policy_url=robots_or_api_policy_url,
            reviewed_at=reviewed_at,
            allowed_data_shape=allowed_data_shape,
            review_notes=review_notes,
            rate_limit_per_minute=rate_limit_per_minute,
            cache_ttl_seconds=cache_ttl_seconds,
            authentication_required=authentication_required,
            authentication_approved=authentication_approved,
            credential_storage_reviewed=credential_storage_reviewed,
            login_required=login_required,
            captcha_gated=captcha_gated,
            private_data_risk=private_data_risk,
        )
        write_connector_review_draft(updated, review_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return ConnectorReviewEvidenceUpdate(review=updated)


__all__ = [
    "ConnectorReviewEvidenceUpdate",
    "update_review_evidence_file",
]
