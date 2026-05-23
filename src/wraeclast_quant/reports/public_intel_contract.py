from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel import PUBLIC_INTEL_SCHEMA_VERSION

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


class PublicIntelContractError(ValueError):
    """Raised when a local public-intel export cannot be loaded."""


@dataclass(frozen=True)
class PublicIntelValidationResult:
    path: Path
    valid: bool
    schema_version: str
    latest_run_id: int | None
    top_opportunities_count: int
    alerts_count: int
    errors: list[str]


def validate_public_intel_file(path: Path) -> PublicIntelValidationResult:
    if not path.exists():
        raise PublicIntelContractError(f"Public intel file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PublicIntelContractError(f"Invalid public intel JSON: {error.msg}") from error

    if not isinstance(payload, dict):
        return PublicIntelValidationResult(
            path=path,
            valid=False,
            schema_version="",
            latest_run_id=None,
            top_opportunities_count=0,
            alerts_count=0,
            errors=["Public intel payload must be a JSON object."],
        )

    errors = validate_public_intel_payload(payload)
    latest_run = payload.get("latest_run") if isinstance(payload.get("latest_run"), dict) else {}
    top_opportunities = payload.get("top_opportunities")
    alerts = payload.get("alerts")

    return PublicIntelValidationResult(
        path=path,
        valid=not errors,
        schema_version=str(payload.get("schema_version", "")),
        latest_run_id=_optional_int(latest_run.get("id")),
        top_opportunities_count=len(top_opportunities) if isinstance(top_opportunities, list) else 0,
        alerts_count=len(alerts) if isinstance(alerts, list) else 0,
        errors=errors,
    )


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


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
