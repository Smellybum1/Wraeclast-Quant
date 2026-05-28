from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository


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
    seen_items: set[str] = set()
    for index, raw_decision in enumerate(raw_decisions, start=1):
        decision = normalize_batch_outcome_decision(index, raw_decision)
        item_name = decision["item_name"]
        if item_name in seen_items:
            raise ValueError(f"decision {index} duplicates item_name '{item_name}'.")
        seen_items.add(item_name)
        decisions.append(decision)
    return run_id, decisions


def normalize_batch_outcome_decision(index: int, raw_decision: Any) -> dict[str, str]:
    if not isinstance(raw_decision, dict):
        raise ValueError(f"decision {index} must be an object.")
    item_name = raw_decision.get("item_name")
    if not isinstance(item_name, str) or not item_name.strip():
        raise ValueError(f"decision {index} must include a non-empty item_name.")
    outcome = raw_decision.get("outcome")
    if not isinstance(outcome, str):
        raise ValueError(f"decision {index} must include an outcome.")
    normalized_outcome = outcome.strip().lower()
    allowed = ", ".join(sorted(ALLOWED_OUTCOMES))
    if not normalized_outcome:
        raise ValueError(
            f"decision {index} outcome is blank; fill it with one of: {allowed}, "
            "then rerun record-outcomes --dry-run."
        )
    if normalized_outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"decision {index} outcome must be one of: {allowed}.")
    notes = raw_decision.get("notes", "")
    if not isinstance(notes, str):
        raise ValueError(f"decision {index} notes must be a string when supplied.")
    return {
        "item_name": item_name.strip(),
        "outcome": normalized_outcome,
        "notes": notes,
    }


def validate_batch_outcome_decisions(
    repository: SnapshotRepository,
    run_id: int,
    decisions: list[dict[str, str]],
) -> None:
    if repository.analysis_run(run_id) is None:
        raise ValueError(f"analysis run #{run_id} was not found")
    item_names = {
        opportunity.item_name
        for opportunity in repository.scored_opportunities_for_run(run_id, limit=None)
    }
    for decision in decisions:
        item_name = decision["item_name"]
        if item_name not in item_names:
            raise ValueError(f"item '{item_name}' was not found in analysis run #{run_id}")
        if repository.recommendation_outcome_exists(run_id, item_name):
            raise ValueError(
                f"item '{item_name}' already has a recorded outcome for analysis run #{run_id}"
            )


__all__ = [
    "load_batch_outcome_decisions",
    "normalize_batch_outcome_decision",
    "validate_batch_outcome_decisions",
]
