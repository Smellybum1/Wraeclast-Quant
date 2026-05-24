from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ALLOWED_ACCESS_METHODS,
    ConnectorReview,
)


def add_review_field_blockers(review: ConnectorReview, blockers: list[str]) -> None:
    if review.access_method not in ALLOWED_ACCESS_METHODS:
        blockers.append(
            "access_method must be one of api, rss, download, or manual-export."
        )
    if not review.source_terms_reviewed:
        blockers.append("Source terms must be reviewed.")
    elif not review.source_terms_url.strip():
        blockers.append("source_terms_url is required when source terms are reviewed.")
    if not review.robots_or_api_policy_reviewed:
        blockers.append("Robots.txt or API policy must be reviewed.")
    elif not review.robots_or_api_policy_url.strip():
        blockers.append(
            "robots_or_api_policy_url is required when robots/API policy is reviewed."
        )
    if review.source_terms_reviewed and review.robots_or_api_policy_reviewed:
        if not review.reviewed_at.strip():
            blockers.append("reviewed_at is required when review confirmations are complete.")
        if not review.allowed_data_shape.strip():
            blockers.append(
                "allowed_data_shape is required when review confirmations are complete."
            )


__all__ = ["add_review_field_blockers"]
