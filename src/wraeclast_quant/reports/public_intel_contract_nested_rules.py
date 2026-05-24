from __future__ import annotations

from typing import Any


def add_nested_shape_errors(payload: dict[str, Any], errors: list[str]) -> None:
    _validate_latest_run(payload, errors)
    _validate_snapshot_changes(payload, errors)
    _validate_compliance_summary(payload, errors)


def _validate_latest_run(payload: dict[str, Any], errors: list[str]) -> None:
    latest_run = payload.get("latest_run")
    if isinstance(latest_run, dict):
        for key in ["id", "created_at", "source_mode", "item_count"]:
            if key not in latest_run:
                errors.append(f"latest_run is missing {key}.")


def _validate_snapshot_changes(payload: dict[str, Any], errors: list[str]) -> None:
    snapshot_changes = payload.get("snapshot_changes")
    if isinstance(snapshot_changes, dict):
        for key in ["top_movers", "status_changes"]:
            if not isinstance(snapshot_changes.get(key), list):
                errors.append(f"snapshot_changes.{key} must be a list.")


def _validate_compliance_summary(payload: dict[str, Any], errors: list[str]) -> None:
    compliance = payload.get("compliance_summary")
    if isinstance(compliance, dict):
        for key in ["total_resources", "status_counts", "automation_eligible_count"]:
            if key not in compliance:
                errors.append(f"compliance_summary is missing {key}.")
        if "status_counts" in compliance and not isinstance(compliance["status_counts"], dict):
            errors.append("compliance_summary.status_counts must be an object.")


__all__ = ["add_nested_shape_errors"]
