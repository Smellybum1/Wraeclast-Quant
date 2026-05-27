from __future__ import annotations


NO_OUTCOME_REVIEWS_MESSAGE = "No reviewed recommendation outcomes found."
NO_OUTCOME_NEXT_STEP = (
    "Next: run wq review-queue --run-id <id> "
    "--output-path data/processed/review_queue.md, "
    "then record human decisions with "
    "wq record-outcome --run-id <id> --item-name <name> "
    "--outcome positive|neutral|negative."
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
