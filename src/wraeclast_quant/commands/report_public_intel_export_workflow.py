from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel import build_public_intel
from wraeclast_quant.storage.repositories import SnapshotRepository


def public_intel_alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return AlertRuleSettings(
            watch_threshold=watch_threshold,
            buy_threshold=buy_threshold,
            big_positive_delta=big_delta,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error


def build_export_payload(
    database_path: Path,
    resources_path: Path,
    limit: int,
    alert_settings: AlertRuleSettings,
) -> dict[str, Any] | None:
    resources = load_resources(resources_path)
    return build_public_intel(
        repository=SnapshotRepository(database_path),
        resources=resources,
        assessments=assess_resources(resources),
        limit=limit,
        alert_settings=alert_settings,
    )


__all__ = [
    "build_export_payload",
    "public_intel_alert_settings",
]
