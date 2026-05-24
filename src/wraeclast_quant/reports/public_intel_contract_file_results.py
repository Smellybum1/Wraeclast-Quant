from __future__ import annotations

from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_contract_file_summary import (
    alerts_count,
    latest_run_id,
    top_opportunities_count,
)
from wraeclast_quant.reports.public_intel_contract_models import PublicIntelValidationResult


def non_object_validation_result(path: Path) -> PublicIntelValidationResult:
    return PublicIntelValidationResult(
        path=path,
        valid=False,
        schema_version="",
        latest_run_id=None,
        top_opportunities_count=0,
        alerts_count=0,
        errors=["Public intel payload must be a JSON object."],
    )


def file_validation_result(
    path: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> PublicIntelValidationResult:
    return PublicIntelValidationResult(
        path=path,
        valid=not errors,
        schema_version=str(payload.get("schema_version", "")),
        latest_run_id=latest_run_id(payload),
        top_opportunities_count=top_opportunities_count(payload),
        alerts_count=alerts_count(payload),
        errors=errors,
    )


__all__ = ["file_validation_result", "non_object_validation_result"]
