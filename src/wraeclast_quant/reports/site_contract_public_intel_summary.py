from __future__ import annotations

from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)


def public_intel_summary(path: Path) -> dict[str, Any]:
    try:
        validation = validate_public_intel_file(path)
    except PublicIntelContractError as error:
        return {
            "valid": False,
            "schema_version": "",
            "latest_run_id": None,
            "top_opportunities": None,
            "alerts": None,
            "error": str(error),
        }
    return {
        "valid": validation.valid,
        "schema_version": validation.schema_version,
        "latest_run_id": validation.latest_run_id,
        "top_opportunities": validation.top_opportunities_count,
        "alerts": validation.alerts_count,
        "errors": validation.errors,
    }


__all__ = ["public_intel_summary"]
