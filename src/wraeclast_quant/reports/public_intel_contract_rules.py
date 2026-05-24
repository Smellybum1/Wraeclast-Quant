from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.public_intel_contract_safety import (
    RAW_FIELD_NAMES,
    URL_RE,
    derived_only_errors,
)
from wraeclast_quant.reports.public_intel_contract_shape import (
    REQUIRED_TOP_LEVEL_KEYS,
    validate_payload_shape,
)


def validate_public_intel_payload(payload: dict[str, Any]) -> list[str]:
    errors = validate_payload_shape(payload)
    errors.extend(derived_only_errors(payload))
    return errors


__all__ = [
    "RAW_FIELD_NAMES",
    "REQUIRED_TOP_LEVEL_KEYS",
    "URL_RE",
    "validate_public_intel_payload",
]
