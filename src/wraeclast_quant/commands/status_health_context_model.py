from __future__ import annotations

from dataclasses import dataclass

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.reports.market_brief import MarketBriefHealthResult
from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult
from wraeclast_quant.reports.static_site import StaticSiteHealthResult
from wraeclast_quant.storage.backups import DatabaseBackupListing
from wraeclast_quant.storage.health import DatabaseHealthResult
from wraeclast_quant.storage.models import AnalysisRunRecord, ReviewCoverageRecord


@dataclass(frozen=True)
class StatusHealthContext:
    resources: list[Resource]
    assessments: list[ComplianceAssessment]
    eligible_count: int
    backups: list[DatabaseBackupListing]
    database_health: DatabaseHealthResult | None
    database_exists: bool
    latest: AnalysisRunRecord | None
    latest_run_id: int | None
    coverage: ReviewCoverageRecord | None
    market_brief_health: MarketBriefHealthResult | None
    intel_validation: PublicIntelValidationResult | None
    intel_error: str
    static_site_health: StaticSiteHealthResult | None
    site_bundle_health: SiteBundleHealthResult | None


__all__ = ["StatusHealthContext"]
