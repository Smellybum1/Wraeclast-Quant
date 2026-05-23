from __future__ import annotations

import zipfile
from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult
from wraeclast_quant.reports.static_site import check_static_site_health


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


def add_public_intel_checks(
    checks: list[PublishCheckRow],
    blockers: list[str],
    intel_path: Path,
) -> int | None:
    try:
        validation = validate_public_intel_file(intel_path)
    except PublicIntelContractError as error:
        add_blocking_check(
            checks,
            blockers,
            "public_intel_contract",
            "Public intel contract",
            "invalid",
            str(error),
        )
        return None
    if not validation.valid:
        add_blocking_check(
            checks,
            blockers,
            "public_intel_contract",
            "Public intel contract",
            "invalid",
            "; ".join(validation.errors),
        )
        return validation.latest_run_id
    checks.append(
        PublishCheckRow(
            key="public_intel_contract",
            check="Public intel contract",
            status="ok",
            details=(
                f"schema {validation.schema_version}; latest run "
                f"#{validation.latest_run_id or 'none'}"
            ),
        )
    )
    return validation.latest_run_id


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


def add_safety_check(
    checks: list[PublishCheckRow],
    blockers: list[str],
    health: SiteBundleHealthResult | None,
) -> None:
    if health is None or not health.valid:
        add_blocking_check(
            checks,
            blockers,
            "derived_only_safety",
            "Derived-only safety",
            "unknown",
            "Bundle manifest must be valid before safety can be confirmed.",
        )
        return
    checks.append(
        PublishCheckRow(
            key="derived_only_safety",
            check="Derived-only safety",
            status="ok",
            details="Bundle manifest confirms derived-only output and no network behavior.",
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
