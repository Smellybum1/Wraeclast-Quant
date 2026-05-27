from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.commands.status_health_context_validation import load_public_intel_validation
from wraeclast_quant.reports.market_brief import MarketBriefHealthResult, check_market_brief_health
from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult, check_site_bundle_health
from wraeclast_quant.reports.stash_ninja_watchlist_health import (
    StashNinjaWatchlistHealthResult,
    check_stash_ninja_watchlist_health,
)
from wraeclast_quant.reports.static_site import StaticSiteHealthResult, check_static_site_health


@dataclass(frozen=True)
class ArtifactStatusContext:
    market_brief_health: MarketBriefHealthResult | None
    intel_validation: PublicIntelValidationResult | None
    intel_error: str
    static_site_health: StaticSiteHealthResult | None
    site_bundle_health: SiteBundleHealthResult | None
    stash_ninja_health: StashNinjaWatchlistHealthResult | None


def load_artifact_status_context(
    *,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
    stash_ninja_path: Path,
) -> ArtifactStatusContext:
    intel_validation, intel_error = load_public_intel_validation(intel_path)
    return ArtifactStatusContext(
        market_brief_health=check_market_brief_health(brief_path),
        intel_validation=intel_validation,
        intel_error=intel_error,
        static_site_health=check_static_site_health(site_dir / "index.html"),
        site_bundle_health=check_site_bundle_health(bundle_dir),
        stash_ninja_health=check_stash_ninja_watchlist_health(stash_ninja_path),
    )


__all__ = ["ArtifactStatusContext", "load_artifact_status_context"]
