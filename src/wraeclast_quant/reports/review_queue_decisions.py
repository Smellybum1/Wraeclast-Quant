from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.models import StoredOpportunityRecord


def review_queue_decisions_payload(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> dict[str, object]:
    return {
        "local_review_only": True,
        "instructions": (
            "Fill each outcome with one of: positive, neutral, negative. "
            "Then run record-outcomes --dry-run before recording."
        ),
        "allowed_outcomes": ["positive", "neutral", "negative"],
        "run_id": run_id,
        "decisions": [
            {
                "item_name": opportunity.item_name,
                "opportunity_score": opportunity.opportunity_score,
                "action": opportunity.action,
                "outcome": "",
                "notes": "",
            }
            for opportunity in opportunities
        ],
    }


def write_review_queue_decisions_template(
    path: Path,
    *,
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> None:
    ensure_outcome_decisions_template_can_be_written(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            review_queue_decisions_payload(run_id, opportunities),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def ensure_outcome_decisions_template_can_be_written(path: Path) -> None:
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "outcome decisions file already exists and could not be safely inspected; "
            f"refusing to overwrite local review work: {path}"
        ) from error
    if _has_outcome_labels(payload):
        raise ValueError(
            "outcome decisions file already contains outcome labels; "
            f"refusing to overwrite local review work: {path}"
        )


def _has_outcome_labels(payload: object) -> bool:
    if not isinstance(payload, dict):
        return True
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        return True
    for decision in decisions:
        if not isinstance(decision, dict):
            return True
        outcome = decision.get("outcome", "")
        if not isinstance(outcome, str):
            return True
        if outcome.strip():
            return True
    return False


__all__ = [
    "ensure_outcome_decisions_template_can_be_written",
    "review_queue_decisions_payload",
    "write_review_queue_decisions_template",
]
