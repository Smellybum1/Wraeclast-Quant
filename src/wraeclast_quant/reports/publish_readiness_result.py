from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckResult, PublishCheckRow
from wraeclast_quant.reports.publish_readiness_paths import PublishReadinessPaths


def publish_readiness_result(
    *,
    paths: PublishReadinessPaths,
    checks: list[PublishCheckRow],
    blockers: list[str],
    latest_database_run_id: int | None,
    bundle_latest_run_id: int | None,
    files: list[str],
) -> PublishCheckResult:
    return PublishCheckResult(
        ready=not blockers,
        latest_database_run_id=latest_database_run_id,
        bundle_latest_run_id=bundle_latest_run_id,
        archive_path=paths.archive_path,
        files=files,
        checks=checks,
        blockers=blockers,
    )


__all__ = ["publish_readiness_result"]
