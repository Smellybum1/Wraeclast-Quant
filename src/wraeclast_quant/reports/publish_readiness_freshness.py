from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_freshness_check


def add_artifact_freshness_checks(
    checks: list[PublishCheckRow],
    blockers: list[str],
    *,
    latest_database_run_id: int | None,
    bundle_latest_run_id: int | None,
    intel_latest_run_id: int | None,
    static_latest_run_id: int | None,
) -> None:
    add_freshness_check(
        checks,
        blockers,
        key="bundle_freshness",
        check="Bundle freshness",
        artifact_label="bundle",
        artifact_run_id=bundle_latest_run_id,
        latest_database_run_id=latest_database_run_id,
    )
    add_freshness_check(
        checks,
        blockers,
        key="public_intel_freshness",
        check="Public intel freshness",
        artifact_label="public intel",
        artifact_run_id=intel_latest_run_id,
        latest_database_run_id=latest_database_run_id,
    )
    add_freshness_check(
        checks,
        blockers,
        key="static_site_freshness",
        check="Static site freshness",
        artifact_label="static site",
        artifact_run_id=static_latest_run_id,
        latest_database_run_id=latest_database_run_id,
    )


__all__ = ["add_artifact_freshness_checks"]
