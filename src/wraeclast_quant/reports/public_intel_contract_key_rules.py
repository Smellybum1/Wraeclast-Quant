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


def key_and_schema_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(payload))
    if missing:
        errors.append("Missing required keys: " + ", ".join(missing))

    if payload.get("schema_version") != PUBLIC_INTEL_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {PUBLIC_INTEL_SCHEMA_VERSION}, "
            f"got {payload.get('schema_version')!r}."
        )
    return errors


__all__ = [
    "REQUIRED_TOP_LEVEL_KEYS",
    "key_and_schema_errors",
]
