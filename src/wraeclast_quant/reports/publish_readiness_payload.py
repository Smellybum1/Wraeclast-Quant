from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckResult


def publish_check_payload(result: PublishCheckResult) -> dict[str, object]:
    return {
        "ready": result.ready,
        "latest_database_run_id": result.latest_database_run_id,
        "bundle_latest_run_id": result.bundle_latest_run_id,
        "checks": [row.__dict__ for row in result.checks],
        "blockers": result.blockers,
    }
