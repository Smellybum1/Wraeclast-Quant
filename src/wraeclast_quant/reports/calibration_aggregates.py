from __future__ import annotations

from wraeclast_quant.reports.calibration_models import SCORE_BUCKETS
from wraeclast_quant.reports.calibration_score_buckets import score_bucket
from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES


def counts_by_action(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for review in reviews:
        if review.action not in summary:
            summary[review.action] = empty_outcome_counts()
        summary[review.action][review.outcome] += 1
    return summary


def counts_by_score_bucket(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary = {bucket: empty_outcome_counts() for bucket in SCORE_BUCKETS}
    for review in reviews:
        summary[score_bucket(review.opportunity_score)][review.outcome] += 1
    return summary


def average_score_by_outcome(reviews: list[OutcomeReviewRecord]) -> dict[str, float | None]:
    scores = {outcome: [] for outcome in sorted(ALLOWED_OUTCOMES)}
    for review in reviews:
        scores[review.outcome].append(review.opportunity_score)
    return {
        outcome: (sum(values) / len(values) if values else None)
        for outcome, values in scores.items()
    }


def empty_outcome_counts() -> dict[str, int]:
    return {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}


__all__ = [
    "average_score_by_outcome",
    "counts_by_action",
    "counts_by_score_bucket",
    "empty_outcome_counts",
]
