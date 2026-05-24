from __future__ import annotations

import re
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
RAW_FIELD_NAMES = {"inputs", "notes", "url", "urls", "resources", "raw_resources"}
URL_RE = re.compile(r"https?://", re.IGNORECASE)


def validate_public_intel_payload(payload: dict[str, Any]) -> list[str]:
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

    latest_run = payload.get("latest_run")
    if isinstance(latest_run, dict):
        for key in ["id", "created_at", "source_mode", "item_count"]:
            if key not in latest_run:
                errors.append(f"latest_run is missing {key}.")

    snapshot_changes = payload.get("snapshot_changes")
    if isinstance(snapshot_changes, dict):
        for key in ["top_movers", "status_changes"]:
            if not isinstance(snapshot_changes.get(key), list):
                errors.append(f"snapshot_changes.{key} must be a list.")

    compliance = payload.get("compliance_summary")
    if isinstance(compliance, dict):
        for key in ["total_resources", "status_counts", "automation_eligible_count"]:
            if key not in compliance:
                errors.append(f"compliance_summary is missing {key}.")
        if "status_counts" in compliance and not isinstance(compliance["status_counts"], dict):
            errors.append("compliance_summary.status_counts must be an object.")

    errors.extend(_derived_only_errors(payload))
    return errors


def _expect_object(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], dict):
        errors.append(f"{key} must be an object.")


def _expect_list(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], list):
        errors.append(f"{key} must be a list.")


def _derived_only_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            child_path = f"{path}.{key}"
            if normalized in RAW_FIELD_NAMES:
                errors.append(f"Raw/private field is not allowed: {child_path}")
            errors.extend(_derived_only_errors(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_derived_only_errors(child, f"{path}[{index}]"))
    elif isinstance(value, str) and URL_RE.search(value):
        errors.append(f"Raw URL is not allowed: {path}")
    return errors
