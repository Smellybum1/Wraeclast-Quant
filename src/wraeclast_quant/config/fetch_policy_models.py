from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from wraeclast_quant.config.connector_policy import ConnectorCheckResult

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
