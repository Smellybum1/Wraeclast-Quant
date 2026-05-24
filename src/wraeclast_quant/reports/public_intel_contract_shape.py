from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.public_intel_contract_key_rules import (
    REQUIRED_TOP_LEVEL_KEYS,
    key_and_schema_errors,
)
from wraeclast_quant.reports.public_intel_contract_type_rules import (
    add_container_type_errors,
    add_nested_shape_errors,
)


def validate_payload_shape(payload: dict[str, Any]) -> list[str]:
    errors = key_and_schema_errors(payload)
    add_container_type_errors(payload, errors)
    add_nested_shape_errors(payload, errors)
    return errors


__all__ = ["REQUIRED_TOP_LEVEL_KEYS", "validate_payload_shape"]
