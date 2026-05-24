from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_contract_models import (
    PublicIntelContractError,
    PublicIntelValidationResult,
)
from wraeclast_quant.reports.public_intel_contract_rules import validate_public_intel_payload


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


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
