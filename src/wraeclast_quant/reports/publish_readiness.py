from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.publish_models import PublishCheckResult, PublishCheckRow
from wraeclast_quant.reports.publish_readiness_database import add_latest_database_run_check
from wraeclast_quant.reports.publish_readiness_freshness import add_artifact_freshness_checks
from wraeclast_quant.reports.publish_readiness_artifacts import (
    add_bundle_checks,
    add_public_intel_checks,
    add_safety_check,
    add_static_site_checks,
    archive_members,
)
from wraeclast_quant.reports.publish_readiness_payload import publish_check_payload
from wraeclast_quant.reports.publish_readiness_paths import publish_readiness_paths
from wraeclast_quant.reports.publish_readiness_result import publish_readiness_result
from wraeclast_quant.reports.publish_readiness_rows import add_manual_publish_readiness
from wraeclast_quant.reports.site_bundle import check_site_bundle_health


def check_publish_readiness(
    database_path: Path,
    bundle_dir: Path,
) -> PublishCheckResult:
    paths = publish_readiness_paths(bundle_dir)

    checks: list[PublishCheckRow] = []
    blockers: list[str] = []
    latest_database_run_id = add_latest_database_run_check(checks, blockers, database_path)

    bundle_health = check_site_bundle_health(paths.bundle_dir)
    files = archive_members(paths.archive_path)
    add_bundle_checks(checks, blockers, bundle_health, paths.archive_path, files)

    intel_latest_run_id = add_public_intel_checks(checks, blockers, paths.intel_path)
    static_latest_run_id = add_static_site_checks(checks, blockers, paths.index_path)
    bundle_latest_run_id = bundle_health.latest_run_id if bundle_health is not None else None

    add_artifact_freshness_checks(
        checks,
        blockers,
        latest_database_run_id=latest_database_run_id,
        bundle_latest_run_id=bundle_latest_run_id,
        intel_latest_run_id=intel_latest_run_id,
        static_latest_run_id=static_latest_run_id,
    )

    add_safety_check(checks, blockers, bundle_health)
    add_manual_publish_readiness(checks, blockers)
    return publish_readiness_result(
        paths=paths,
        checks=checks,
        blockers=blockers,
        latest_database_run_id=latest_database_run_id,
        bundle_latest_run_id=bundle_latest_run_id,
        files=files,
    )
