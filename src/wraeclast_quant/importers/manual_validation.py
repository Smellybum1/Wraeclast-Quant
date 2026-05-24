from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from wraeclast_quant.importers.manual_models import ManualImportError, SIGNAL_FIELDS
from wraeclast_quant.intelligence.scoring import OpportunityInputs


def validate_item(item: Any, index: int) -> dict[str, object]:
    if not isinstance(item, dict):
        raise ManualImportError(f"Item {index} must be an object.")

    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ManualImportError(f"Item {index} is missing a non-empty name.")

    signals = item.get("signals")
    if not isinstance(signals, dict):
        raise ManualImportError(f"Item {index} is missing a signals object.")

    missing_signals = [field for field in SIGNAL_FIELDS if field not in signals]
    if missing_signals:
        raise ManualImportError(
            f"Item {index} is missing required signals: {', '.join(missing_signals)}"
        )

    try:
        inputs = OpportunityInputs(**{field: signals[field] for field in SIGNAL_FIELDS})
    except ValidationError as error:
        details = "; ".join(
            f"{'.'.join(str(part) for part in issue['loc'])}: {issue['msg']}"
            for issue in error.errors()
        )
        raise ManualImportError(f"Item {index} has invalid signals: {details}") from error

    return {"name": name.strip(), "signals": inputs.model_dump()}
