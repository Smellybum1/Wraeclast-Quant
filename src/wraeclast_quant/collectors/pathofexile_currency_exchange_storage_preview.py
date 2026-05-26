from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.config.fetch_policy_cache import cache_path_for
from wraeclast_quant.config.resources_loader import Resource


@dataclass(frozen=True)
class CurrencyExchangeStoragePlan:
    resource_id: str
    raw_cache_path: Path
    baseline_observations_path: Path
    baseline_diagnostics_path: Path
    cache_ttl_seconds: int
    stores_credentials: bool = False
    writes_enabled: bool = False


def preview_currency_exchange_storage_plan(
    *,
    resource_id: str = "official_currency_exchange_api",
    resource_name: str = "Path of Exile Currency Exchange API",
    resource_url: str = "https://www.pathofexile.com/developer/docs/reference",
    cache_root: str | Path = Path("data/raw/cache"),
    processed_root: str | Path = Path("data/processed/currency_exchange"),
    cache_ttl_seconds: int = 3600,
) -> CurrencyExchangeStoragePlan:
    resource = Resource(
        id=resource_id,
        name=resource_name,
        url=resource_url,
        allowed_use="api",
    )
    processed_base = Path(processed_root)
    return CurrencyExchangeStoragePlan(
        resource_id=resource_id,
        raw_cache_path=cache_path_for(resource, Path(cache_root)),
        baseline_observations_path=processed_base / "baseline_observations.preview.json",
        baseline_diagnostics_path=processed_base / "baseline_diagnostics.preview.json",
        cache_ttl_seconds=cache_ttl_seconds,
    )


__all__ = [
    "CurrencyExchangeStoragePlan",
    "preview_currency_exchange_storage_plan",
]
