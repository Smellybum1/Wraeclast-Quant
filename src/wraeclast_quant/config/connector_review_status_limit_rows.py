from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorReview,
    ConnectorReviewStatusRow,
)


def limit_status_rows(review: ConnectorReview) -> list[ConnectorReviewStatusRow]:
    return [
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
    ]
