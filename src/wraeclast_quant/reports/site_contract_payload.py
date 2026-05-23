from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.publish_check import (
    PublishCheckResult,
    check_publish_readiness,
    publish_check_payload,
)
from wraeclast_quant.reports.site_bundle import REQUIRED_ARCHIVE_MEMBERS
from wraeclast_quant.reports.site_contract_constants import (
    SAFETY_STATEMENT,
    SITE_CONTRACT_SCHEMA_VERSION,
)
from wraeclast_quant.reports.site_contract_summaries import (
    bundle_summary,
    public_intel_summary,
    static_site_summary,
)


def build_site_contract(
    database_path: Path,
    bundle_dir: Path,
) -> dict[str, Any]:
    readiness = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)
    return site_contract_payload(readiness, bundle_dir)


def site_contract_payload(
    readiness: PublishCheckResult,
    bundle_dir: Path,
) -> dict[str, Any]:
    public_intel = public_intel_summary(bundle_dir / "public_intel.json")
    static_site = static_site_summary(bundle_dir / "index.html")
    bundle = bundle_summary(bundle_dir)

    return {
        "schema_version": SITE_CONTRACT_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "product": "Wraeclast Quant",
        "latest_database_run_id": readiness.latest_database_run_id,
        "artifact_run_ids": {
            "bundle": readiness.bundle_latest_run_id,
            "public_intel": public_intel["latest_run_id"],
            "static_site": static_site["latest_run_id"],
        },
        "public_intel": public_intel,
        "static_site": static_site,
        "bundle": bundle,
        "required_bundle_files": sorted(REQUIRED_ARCHIVE_MEMBERS),
        "publish_readiness": publish_check_payload(readiness),
        "safety": {
            "derived_only": True,
            "network_behavior": "none",
            "publishing_behavior": "manual-outside-app-only",
            "statement": SAFETY_STATEMENT,
        },
    }
