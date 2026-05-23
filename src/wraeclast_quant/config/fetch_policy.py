from __future__ import annotations

import hashlib
import re
from pathlib import Path

from pydantic import BaseModel

from wraeclast_quant.config.connector_policy import (
    ConnectorCheckResult,
    ConnectorReview,
    check_connector_review,
)
from wraeclast_quant.config.resources_loader import Resource

DEFAULT_CACHE_ROOT = Path("data/raw/cache")


class FetchPlan(BaseModel):
    resource_name: str
    url: str
    access_method: str
    cache_ttl_seconds: int
    rate_limit_per_minute: float
    min_seconds_between_requests: float
    cache_path: Path
    dry_run_required: bool = True
    public_export_derived_only: bool = True


class FetchPlanResult(BaseModel):
    check: ConnectorCheckResult
    plan: FetchPlan | None


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
            cache_path=_cache_path_for(check.resource, cache_root),
            dry_run_required=True,
            public_export_derived_only=True,
        ),
    )


def _cache_path_for(resource: Resource, cache_root: Path) -> Path:
    safe_name = _safe_slug(resource.name or resource.id or "resource")
    digest = hashlib.sha256(resource.url.encode("utf-8")).hexdigest()[:12]
    return cache_root / f"{safe_name}-{digest}.cache"


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug[:60] or "resource"
