from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.publish_check import PublishCheckResult
from wraeclast_quant.reports.site_contract_constants import SAFETY_STATEMENT


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


def safety_payload() -> dict[str, object]:
    return {
        "derived_only": True,
        "network_behavior": "none",
        "publishing_behavior": "manual-outside-app-only",
        "statement": SAFETY_STATEMENT,
    }


__all__ = ["artifact_run_ids", "safety_payload"]
