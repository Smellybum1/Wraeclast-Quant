from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.publish_check import PublishCheckResult


def artifact_run_ids(
    readiness: PublishCheckResult,
    public_intel: dict[str, Any],
    static_site: dict[str, Any],
) -> dict[str, int | None]:
    return {
        "bundle": readiness.bundle_latest_run_id,
        "public_intel": public_intel["latest_run_id"],
        "static_site": static_site["latest_run_id"],
    }


__all__ = ["artifact_run_ids"]
