from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.market_brief import MarketBriefHealthResult
from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult
from wraeclast_quant.reports.site_bundle import ARCHIVE_NAME, SiteBundleHealthResult
from wraeclast_quant.reports.static_site import StaticSiteHealthResult


def public_intel_status(
    path: Path,
    validation: PublicIntelValidationResult | None,
    error: str,
) -> str:
    if not path.exists():
        return "no"
    if error or validation is None or not validation.valid:
        return "needs attention"
    return "ok"


def public_intel_details(
    path: Path,
    validation: PublicIntelValidationResult | None,
    error: str,
    latest_database_run_id: int | None,
) -> str:
    if not path.exists():
        return str(path)
    if error:
        return f"{path}; {error}"
    if validation is None:
        return f"{path}; validation did not run"
    if not validation.valid:
        return f"{path}; " + "; ".join(validation.errors)
    details = (
        f"{path}; schema {validation.schema_version}; "
        f"latest run #{validation.latest_run_id or 'none'}; "
        f"{validation.top_opportunities_count} opportunities; "
        f"{validation.alerts_count} alerts"
    )
    return details + fresh_artifact_details(
        artifact_run_id=validation.latest_run_id,
        latest_database_run_id=latest_database_run_id,
        artifact_label="artifact",
        guidance="run wq export and wq site",
    )


def market_brief_status(health: MarketBriefHealthResult | None) -> str:
    if health is None:
        return "no"
    return "ok" if health.valid else "needs attention"


def market_brief_details(
    path: Path,
    health: MarketBriefHealthResult | None,
) -> str:
    if health is None:
        return str(path)
    if not health.valid:
        return f"{health.path}; missing markers: {', '.join(health.missing_markers)}"
    snapshot = "with snapshot changes" if health.includes_snapshot_changes else "no snapshot changes"
    return f"{health.path}; {snapshot}; {health.size_bytes} bytes"


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
        return f"{health.archive_path}; " + "; ".join(health.errors)
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


def public_intel_run_id(validation: PublicIntelValidationResult | None) -> int | None:
    return validation.latest_run_id if validation is not None and validation.valid else None


def static_site_run_id(health: StaticSiteHealthResult | None) -> int | None:
    return health.latest_run_id if health is not None and health.valid else None


def site_bundle_run_id(health: SiteBundleHealthResult | None) -> int | None:
    return health.latest_run_id if health is not None and health.valid else None


def fresh_artifact_status(
    status_value: str,
    artifact_run_id: int | None,
    latest_database_run_id: int | None,
) -> str:
    if status_value != "ok":
        return status_value
    if artifact_run_id is None or latest_database_run_id is None:
        return status_value
    if artifact_run_id != latest_database_run_id:
        return "needs attention"
    return status_value


def fresh_artifact_details(
    artifact_run_id: int | None,
    latest_database_run_id: int | None,
    artifact_label: str,
    guidance: str,
) -> str:
    if artifact_run_id is None or latest_database_run_id is None:
        return ""
    if artifact_run_id == latest_database_run_id:
        return ""
    return (
        f"; stale; latest database run #{latest_database_run_id}, "
        f"{artifact_label} run #{artifact_run_id}; {guidance}"
    )
