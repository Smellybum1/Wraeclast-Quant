from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.commands.maintenance_outcome_batch_decision_validation import (
    format_batch_outcome_decision_errors,
    normalize_batch_outcome_decision,
    validate_batch_outcome_decisions,
)


def load_batch_outcome_decisions(input_path: Path) -> tuple[int, list[dict[str, str]]]:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"could not read outcome decisions: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid outcome decisions JSON: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError("outcome decisions must be a JSON object.")
    run_id = payload.get("run_id")
    if not isinstance(run_id, int) or run_id < 1:
        raise ValueError("outcome decisions must include a positive integer run_id.")
    raw_decisions = payload.get("decisions")
    if not isinstance(raw_decisions, list) or not raw_decisions:
        raise ValueError("outcome decisions must include a non-empty decisions list.")

    decisions: list[dict[str, str]] = []
    seen_items: dict[str, int] = {}
    errors: list[str] = []
    for index, raw_decision in enumerate(raw_decisions, start=1):
        try:
            decision = normalize_batch_outcome_decision(index, raw_decision)
        except ValueError as error:
            errors.append(str(error))
            continue
        item_name = decision["item_name"]
        if item_name in seen_items:
            errors.append(
                f"decision {index} duplicates item_name '{item_name}' "
                f"(first seen at decision {seen_items[item_name]})."
            )
            continue
        seen_items[item_name] = index
        decisions.append(decision)
    if errors:
        raise ValueError(format_batch_outcome_decision_errors(errors))
    return run_id, decisions


__all__ = [
    "load_batch_outcome_decisions",
    "format_batch_outcome_decision_errors",
    "normalize_batch_outcome_decision",
    "validate_batch_outcome_decisions",
]
