from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ALLOWED_ACCESS_METHODS,
    ConnectorCheckResult,
    ConnectorReview,
    ConnectorReviewStatusRow,
)


def core_status_rows(
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
    ]
