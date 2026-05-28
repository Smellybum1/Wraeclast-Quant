from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_freshness import fresh_artifact_details
from wraeclast_quant.reports.site_bundle import ARCHIVE_NAME, SiteBundleHealthResult


def site_bundle_status(health: SiteBundleHealthResult | None) -> str:
    if health is None:
        return "no"
    return "ok" if health.valid else "needs attention"


def site_bundle_details(
    bundle_dir: Path,
    health: SiteBundleHealthResult | None,
    latest_database_run_id: int | None,
) -> str:
    archive_path = bundle_dir / ARCHIVE_NAME
    if health is None:
        return str(archive_path)
    if not health.valid:
        return "; ".join(health.errors) + f"; {health.archive_path}"
    details = (
        f"{health.archive_path}; schema {health.schema_version or 'unknown'}; "
        f"latest run #{health.latest_run_id or 'none'}; "
        f"{health.top_opportunities_count or 0} opportunities; "
        f"{health.alerts_count or 0} alerts; {health.archive_size_bytes} bytes"
    )
    return details + fresh_artifact_details(
        artifact_run_id=health.latest_run_id,
        latest_database_run_id=latest_database_run_id,
        artifact_label="bundle",
        guidance="run wq site-bundle",
    )


def site_bundle_run_id(health: SiteBundleHealthResult | None) -> int | None:
    return health.latest_run_id if health is not None and health.valid else None
