from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check
from wraeclast_quant.reports.static_site import check_static_site_health


def add_static_site_checks(
    checks: list[PublishCheckRow],
    blockers: list[str],
    index_path: Path,
) -> int | None:
    health = check_static_site_health(index_path)
    if health is None:
        add_blocking_check(
            checks,
            blockers,
            "static_site_metadata",
            "Static site metadata",
            "missing",
            f"{index_path} not found.",
        )
        return None
    if not health.valid:
        add_blocking_check(
            checks,
            blockers,
            "static_site_metadata",
            "Static site metadata",
            "invalid",
            "missing markers: " + ", ".join(health.missing_markers),
        )
        return health.latest_run_id
    checks.append(
        PublishCheckRow(
            key="static_site_metadata",
            check="Static site metadata",
            status="ok",
            details=f"schema {health.schema_version}; latest run #{health.latest_run_id or 'none'}",
        )
    )
    return health.latest_run_id


__all__ = ["add_static_site_checks"]
