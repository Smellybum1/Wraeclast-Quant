from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_freshness import fresh_artifact_details
from wraeclast_quant.reports.static_site import StaticSiteHealthResult


def static_site_status(health: StaticSiteHealthResult | None) -> str:
    if health is None:
        return "no"
    return "ok" if health.valid else "needs attention"


def static_site_details(
    path: Path,
    health: StaticSiteHealthResult | None,
    latest_database_run_id: int | None,
) -> str:
    if health is None:
        return str(path)
    if not health.valid:
        return f"{health.path}; missing markers: {', '.join(health.missing_markers)}"
    details = (
        f"{health.path}; schema {health.schema_version or 'unknown'}; "
        f"latest run #{health.latest_run_id or 'none'}; {health.size_bytes} bytes"
    )
    return details + fresh_artifact_details(
        artifact_run_id=health.latest_run_id,
        latest_database_run_id=latest_database_run_id,
        artifact_label="artifact",
        guidance="run wq site",
    )


def static_site_run_id(health: StaticSiteHealthResult | None) -> int | None:
    return health.latest_run_id if health is not None and health.valid else None
