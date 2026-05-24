from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.public_intel_contract_nested_rules import add_nested_shape_errors


def add_container_type_errors(payload: dict[str, Any], errors: list[str]) -> None:
    _expect_object(payload, "latest_run", errors)
    _expect_object(payload, "snapshot_changes", errors)
    _expect_object(payload, "outcome_summary", errors)
    _expect_object(payload, "review_coverage", errors)
    _expect_object(payload, "compliance_summary", errors)
    for key in ["recent_runs", "top_opportunities", "score_trends", "alerts"]:
        _expect_list(payload, key, errors)

def _expect_object(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], dict):
        errors.append(f"{key} must be an object.")


def _expect_list(payload: dict[str, Any], key: str, errors: list[str]) -> None:
    if key in payload and not isinstance(payload[key], list):
        errors.append(f"{key} must be a list.")


__all__ = [
    "add_container_type_errors",
    "add_nested_shape_errors",
]
