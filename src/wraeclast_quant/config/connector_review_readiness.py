from __future__ import annotations

from wraeclast_quant.config.connector_review_field_readiness import add_review_field_blockers
from wraeclast_quant.config.connector_review_resource_readiness import resource_readiness
from wraeclast_quant.config.connector_review_safety_readiness import add_review_safety_blockers
from wraeclast_quant.config.connector_policy_models import (
    ConnectorCheckResult,
    ConnectorReview,
)
from wraeclast_quant.config.resources_loader import Resource


def check_connector_review(
    review: ConnectorReview,
    resources: list[Resource],
) -> ConnectorCheckResult:
    blockers: list[str] = []
    resource, preflight = resource_readiness(review, resources, blockers)
    add_review_field_blockers(review, blockers)
    add_review_safety_blockers(review, blockers)

    return ConnectorCheckResult(
        review=review,
        resource=resource,
        preflight=preflight,
        ready=not blockers,
        blockers=blockers,
    )
