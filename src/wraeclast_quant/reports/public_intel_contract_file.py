from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.public_intel_contract_models import (
    PublicIntelContractError,
    PublicIntelValidationResult,
)
from wraeclast_quant.reports.public_intel_contract_file_results import (
    file_validation_result,
    non_object_validation_result,
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
        return non_object_validation_result(path)

    errors = validate_public_intel_payload(payload)
    return file_validation_result(path, payload, errors)


__all__ = ["validate_public_intel_file"]
