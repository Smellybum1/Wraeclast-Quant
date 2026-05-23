from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifacts import (
    fresh_artifact_status,
    market_brief_details,
    market_brief_status,
    public_intel_details,
    public_intel_run_id,
    public_intel_status,
    site_bundle_details,
    site_bundle_run_id,
    site_bundle_status,
    static_site_details,
    static_site_run_id,
    static_site_status,
)
from wraeclast_quant.commands.status_health_models import (
    STATUS_JSON_SCHEMA_VERSION,
    StatusHealthReport,
)
from wraeclast_quant.commands.status_health_rows import (
    add_status_row,
    strict_failure_keys,
)
from wraeclast_quant.commands.status_health_storage import (
    backup_status,
    backup_status_details,
    database_health_details,
    database_health_status,
    exists_label,
    latest_run_empty_details,
)
from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources
from wraeclast_quant.reports.market_brief import check_market_brief_health
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle import (
    DEFAULT_SITE_BUNDLE_DIR,
    check_site_bundle_health,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR, check_static_site_health
from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR, list_database_backups
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.health import check_database_health
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_status_report(
    *,
    database_path: Path = DEFAULT_DATABASE_PATH,
    resources_path: Path = Path("RESOURCES.md"),
    brief_path: Path = Path("data/processed/market_brief.md"),
    intel_path: Path = DEFAULT_PUBLIC_INTEL_PATH,
    site_dir: Path = DEFAULT_SITE_DIR,
    bundle_dir: Path = DEFAULT_SITE_BUNDLE_DIR,
    backup_dir: Path = DEFAULT_BACKUP_DIR,
) -> StatusHealthReport:
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
    database_exists = database_path.exists()
    market_brief_health = check_market_brief_health(brief_path)
    static_site_health = check_static_site_health(site_dir / "index.html")
    site_bundle_health = check_site_bundle_health(bundle_dir)
    if database_health is not None and database_health.ok:
        repository = SnapshotRepository(database_path)
        latest = repository.latest_run()
        if latest is not None:
            coverage = repository.review_coverage_for_run(latest.id)
    latest_run_id = latest.id if latest is not None else None

    status_rows: list[dict[str, str]] = []
    strict_rows: list[tuple[str, str]] = []
    add_status_row(
        status_rows,
        "Resources",
        "ok",
        f"{len(resources)} configured; {eligible_count} automation-eligible",
    )
    add_status_row(status_rows, "Database", exists_label(database_exists), str(database_path))
    database_health_row_status = database_health_status(database_health)
    strict_rows.append(("Database health", database_health_row_status))
    add_status_row(
        status_rows,
        "Database health",
        database_health_row_status,
        database_health_details(database_health),
    )
    if latest is None:
        add_status_row(status_rows, "Latest run", "none", latest_run_empty_details(database_health))
        add_status_row(status_rows, "Review coverage", "none", "No latest run.")
    else:
        add_status_row(
            status_rows,
            "Latest run",
            "ok",
            f"#{latest.id} {latest.source_mode}; {latest.item_count} items; {latest.created_at}",
        )
        if coverage is not None:
            add_status_row(
                status_rows,
                "Review coverage",
                "ok",
                (
                    f"{coverage.reviewed_recommendations}/"
                    f"{coverage.total_recommendations} reviewed; "
                    f"{coverage.reviewed_percent:.1f}%; "
                    f"{coverage.unreviewed_recommendations} unreviewed"
                ),
            )
    market_brief_row_status = market_brief_status(market_brief_health)
    public_intel_row_status = fresh_artifact_status(
        public_intel_status(intel_path, intel_validation, intel_error),
        public_intel_run_id(intel_validation),
        latest_run_id,
    )
    static_site_row_status = fresh_artifact_status(
        static_site_status(static_site_health),
        static_site_run_id(static_site_health),
        latest_run_id,
    )
    site_bundle_row_status = fresh_artifact_status(
        site_bundle_status(site_bundle_health),
        site_bundle_run_id(site_bundle_health),
        latest_run_id,
    )
    strict_rows.extend(
        [
            ("Market brief", market_brief_row_status),
            ("Public intel", public_intel_row_status),
            ("Static site", static_site_row_status),
            ("Site bundle", site_bundle_row_status),
        ]
    )
    add_status_row(status_rows, "Market brief", market_brief_row_status, market_brief_details(brief_path, market_brief_health))
    add_status_row(
        status_rows,
        "Public intel",
        public_intel_row_status,
        public_intel_details(intel_path, intel_validation, intel_error, latest_run_id),
    )
    add_status_row(
        status_rows,
        "Static site",
        static_site_row_status,
        static_site_details(site_dir / "index.html", static_site_health, latest_run_id),
    )
    add_status_row(
        status_rows,
        "Site bundle",
        site_bundle_row_status,
        site_bundle_details(bundle_dir, site_bundle_health, latest_run_id),
    )
    backup_row_status = backup_status(backups)
    strict_rows.append(("Backups", backup_row_status))
    add_status_row(status_rows, "Backups", backup_row_status, backup_status_details(backups))
    add_status_row(
        status_rows,
        "Safety boundary",
        "ok",
        "Local-only status check; collectors remain dry-run placeholders.",
    )
    strict_failures = [label for label, row_status in strict_rows if row_status == "needs attention"]
    return StatusHealthReport(
        rows=status_rows,
        strict_failures=strict_failures,
        strict_failure_keys=strict_failure_keys(strict_failures),
    )
