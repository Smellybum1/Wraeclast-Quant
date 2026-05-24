from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_policy import (
    ConnectorReview,
    check_connector_review,
)
from wraeclast_quant.config.fetch_policy_cache import cache_path_for
from wraeclast_quant.config.fetch_policy_models import (
    DEFAULT_CACHE_ROOT,
    FetchPlan,
    FetchPlanResult,
)
from wraeclast_quant.config.resources_loader import Resource


def build_fetch_plan(
    review: ConnectorReview,
    resources: list[Resource],
    cache_root: Path = DEFAULT_CACHE_ROOT,
) -> FetchPlanResult:
    check = check_connector_review(review, resources)
    blockers = list(check.blockers)
    if check.resource is not None and not check.resource.url.strip():
        blockers.append("Resource URL is required for a fetch plan.")

    if blockers:
        return FetchPlanResult(
            check=check.model_copy(update={"ready": False, "blockers": blockers}),
            plan=None,
        )

    assert check.resource is not None
    min_interval = 60.0 / review.rate_limit_per_minute
    return FetchPlanResult(
        check=check,
        plan=FetchPlan(
            resource_name=check.resource.name,
            url=check.resource.url,
            access_method=review.access_method,
            cache_ttl_seconds=review.cache_ttl_seconds,
            rate_limit_per_minute=review.rate_limit_per_minute,
            min_seconds_between_requests=min_interval,
            cache_path=cache_path_for(check.resource, cache_root),
            dry_run_required=True,
            public_export_derived_only=True,
        ),
    )
