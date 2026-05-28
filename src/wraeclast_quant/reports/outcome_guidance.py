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
LOCAL_REPORT_NEXT_ACTION = (
    "Local report artifact only. Run wq status --strict and wq publish-check "
    "before any manual handoff."
)


def no_outcome_review_lines() -> list[str]:
    return [
        NO_OUTCOME_REVIEWS_MESSAGE,
        "",
        NO_OUTCOME_NEXT_STEP,
        OUTCOME_LABEL_GUIDE,
        "",
    ]


def local_report_next_action() -> str:
    return LOCAL_REPORT_NEXT_ACTION


__all__ = [
    "LOCAL_REPORT_NEXT_ACTION",
    "NO_OUTCOME_NEXT_STEP",
    "NO_OUTCOME_REVIEWS_MESSAGE",
    "OUTCOME_LABEL_GUIDE",
    "local_report_next_action",
    "no_outcome_review_lines",
]
