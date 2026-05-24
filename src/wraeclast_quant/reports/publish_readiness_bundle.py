from __future__ import annotations

import zipfile
from pathlib import Path

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult


def add_bundle_checks(
    checks: list[PublishCheckRow],
    blockers: list[str],
    health: SiteBundleHealthResult | None,
    archive_path: Path,
    files: list[str],
) -> None:
    if health is None:
        add_blocking_check(
            checks,
            blockers,
            "site_bundle",
            "Site bundle",
            "missing",
            f"{archive_path} not found.",
        )
        return
    if not health.valid:
        add_blocking_check(
            checks,
            blockers,
            "site_bundle",
            "Site bundle",
            "invalid",
            "; ".join(health.errors),
        )
        return
    checks.append(
        PublishCheckRow(
            key="site_bundle",
            check="Site bundle",
            status="ok",
            details=f"{health.archive_path}; {health.archive_size_bytes} bytes",
        )
    )
    checks.append(
        PublishCheckRow(
            key="bundle_files",
            check="Bundle files",
            status="ok",
            details=", ".join(files),
        )
    )


def archive_members(archive_path: Path) -> list[str]:
    if not archive_path.exists():
        return []
    try:
        with zipfile.ZipFile(archive_path) as archive:
            return sorted(archive.namelist())
    except zipfile.BadZipFile:
        return []
