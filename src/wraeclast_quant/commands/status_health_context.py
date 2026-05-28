from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_context_artifacts import load_artifact_status_context
from wraeclast_quant.commands.status_health_context_database import load_database_status_context
from wraeclast_quant.commands.status_health_context_model import StatusHealthContext
from wraeclast_quant.commands.status_health_context_resources import load_resource_status_context
from wraeclast_quant.commands.status_health_context_snapshots import load_snapshot_status_context


def load_status_health_context(
    *,
    database_path: Path,
    resources_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
    stash_ninja_path: Path,
    backup_dir: Path,
) -> StatusHealthContext:
    resource_context = load_resource_status_context(resources_path)
    database_context = load_database_status_context(database_path=database_path, backup_dir=backup_dir)
    snapshot_context = load_snapshot_status_context(database_path, database_context.database_health)
    artifact_context = load_artifact_status_context(
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        stash_ninja_path=stash_ninja_path,
    )

    return StatusHealthContext(
        resources=resource_context.resources,
        assessments=resource_context.assessments,
        eligible_count=resource_context.eligible_count,
        backups=database_context.backups,
        database_health=database_context.database_health,
        database_exists=database_context.database_exists,
        latest=snapshot_context.latest,
        latest_run_id=snapshot_context.latest_run_id,
        coverage=snapshot_context.coverage,
        calibration_prompts=snapshot_context.calibration_prompts,
        market_brief_health=artifact_context.market_brief_health,
        intel_validation=artifact_context.intel_validation,
        intel_error=artifact_context.intel_error,
        static_site_health=artifact_context.static_site_health,
        site_bundle_health=artifact_context.site_bundle_health,
        stash_ninja_health=artifact_context.stash_ninja_health,
    )


__all__ = ["StatusHealthContext", "load_status_health_context"]
