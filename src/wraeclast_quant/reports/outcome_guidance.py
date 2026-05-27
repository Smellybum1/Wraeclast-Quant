from __future__ import annotations

from wraeclast_quant.reports.review_queue_commands import (
    batch_outcome_review_next_action,
    record_outcomes_command,
)


NO_OUTCOME_REVIEWS_MESSAGE = "No reviewed recommendation outcomes found."
NO_OUTCOME_NEXT_STEP = (
    f"Next: {batch_outcome_review_next_action('<id>')}. "
    f"After the dry-run passes, record the reviewed batch with {record_outcomes_command()}."
)
OUTCOME_LABEL_GUIDE = (
    "Outcome labels: positive=useful signal, neutral=mixed or unclear, "
    "negative=not useful after review."
)


def no_outcome_review_lines() -> list[str]:
    return [
        NO_OUTCOME_REVIEWS_MESSAGE,
        "",
        NO_OUTCOME_NEXT_STEP,
        OUTCOME_LABEL_GUIDE,
        "",
    ]


__all__ = [
    "NO_OUTCOME_NEXT_STEP",
    "NO_OUTCOME_REVIEWS_MESSAGE",
    "OUTCOME_LABEL_GUIDE",
    "no_outcome_review_lines",
]
