from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_context_model import StatusHealthContext
from wraeclast_quant.commands.status_health_context_resources import load_resource_status_context
from wraeclast_quant.commands.status_health_context_snapshots import load_snapshot_status_context
from wraeclast_quant.commands.status_health_context_validation import load_public_intel_validation
from wraeclast_quant.reports.market_brief import check_market_brief_health
from wraeclast_quant.reports.site_bundle import check_site_bundle_health
from wraeclast_quant.reports.static_site import check_static_site_health
from wraeclast_quant.storage.backups import list_database_backups
from wraeclast_quant.storage.health import check_database_health


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
    resource_context = load_resource_status_context(resources_path)
    backups = list_database_backups(backup_dir=backup_dir, limit=1)
    database_health = check_database_health(database_path)
    intel_validation, intel_error = load_public_intel_validation(intel_path)
    snapshot_context = load_snapshot_status_context(database_path, database_health)

    return StatusHealthContext(
        resources=resource_context.resources,
        assessments=resource_context.assessments,
        eligible_count=resource_context.eligible_count,
        backups=backups,
        database_health=database_health,
        database_exists=database_path.exists(),
        latest=snapshot_context.latest,
        latest_run_id=snapshot_context.latest_run_id,
        coverage=snapshot_context.coverage,
        market_brief_health=check_market_brief_health(brief_path),
        intel_validation=intel_validation,
        intel_error=intel_error,
        static_site_health=check_static_site_health(site_dir / "index.html"),
        site_bundle_health=check_site_bundle_health(bundle_dir),
    )


__all__ = ["StatusHealthContext", "load_status_health_context"]
