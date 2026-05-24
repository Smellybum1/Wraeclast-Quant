from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.config.compliance import ComplianceAssessment, assess_resources
from wraeclast_quant.config.resources_loader import Resource, load_resources
from wraeclast_quant.reports.market_brief import MarketBriefHealthResult, check_market_brief_health
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    PublicIntelValidationResult,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult, check_site_bundle_health
from wraeclast_quant.reports.static_site import StaticSiteHealthResult, check_static_site_health
from wraeclast_quant.storage.backups import DatabaseBackupListing, list_database_backups
from wraeclast_quant.storage.health import DatabaseHealthResult, check_database_health
from wraeclast_quant.storage.models import AnalysisRunRecord, ReviewCoverageRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


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


def load_status_health_context(
    *,
    database_path: Path,
    resources_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
    backup_dir: Path,
) -> StatusHealthContext:
    resources = load_resources(resources_path)
    assessments = assess_resources(resources)
    eligible_count = sum(1 for assessment in assessments if assessment.automation_eligible)
    backups = list_database_backups(backup_dir=backup_dir, limit=1)
    database_health = check_database_health(database_path)

    intel_validation = None
    intel_error = ""
    if intel_path.exists():
        try:
            intel_validation = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            intel_error = str(error)

    latest = None
    coverage = None
    if database_health is not None and database_health.ok:
        repository = SnapshotRepository(database_path)
        latest = repository.latest_run()
        if latest is not None:
            coverage = repository.review_coverage_for_run(latest.id)

    return StatusHealthContext(
        resources=resources,
        assessments=assessments,
        eligible_count=eligible_count,
        backups=backups,
        database_health=database_health,
        database_exists=database_path.exists(),
        latest=latest,
        latest_run_id=latest.id if latest is not None else None,
        coverage=coverage,
        market_brief_health=check_market_brief_health(brief_path),
        intel_validation=intel_validation,
        intel_error=intel_error,
        static_site_health=check_static_site_health(site_dir / "index.html"),
        site_bundle_health=check_site_bundle_health(bundle_dir),
    )
