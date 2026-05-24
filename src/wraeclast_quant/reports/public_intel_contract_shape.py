from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.public_intel_constants import PUBLIC_INTEL_SCHEMA_VERSION

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "generated_at",
    "latest_run",
    "recent_runs",
    "top_opportunities",
    "score_trends",
    "snapshot_changes",
    "alerts",
    "outcome_summary",
    "review_coverage",
    "compliance_summary",
}


def validate_payload_shape(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(payload))
    if missing:
        errors.append("Missing required keys: " + ", ".join(missing))

    if payload.get("schema_version") != PUBLIC_INTEL_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {PUBLIC_INTEL_SCHEMA_VERSION}, "
            f"got {payload.get('schema_version')!r}."
        )

    _expect_object(payload, "latest_run", errors)
    _expect_object(payload, "snapshot_changes", errors)
    _expect_object(payload, "outcome_summary", errors)
    _expect_object(payload, "review_coverage", errors)
    _expect_object(payload, "compliance_summary", errors)
    for key in ["recent_runs", "top_opportunities", "score_trends", "alerts"]:
        _expect_list(payload, key, errors)

    _validate_latest_run(payload, errors)
    _validate_snapshot_changes(payload, errors)
    _validate_compliance_summary(payload, errors)
    return errors


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


def _expect_object(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], dict):
        errors.append(f"{key} must be an object.")


def _expect_list(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], list):
        errors.append(f"{key} must be a list.")


__all__ = ["REQUIRED_TOP_LEVEL_KEYS", "validate_payload_shape"]
