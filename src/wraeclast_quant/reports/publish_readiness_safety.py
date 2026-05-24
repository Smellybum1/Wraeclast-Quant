from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check
from wraeclast_quant.reports.site_bundle import SiteBundleHealthResult


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
