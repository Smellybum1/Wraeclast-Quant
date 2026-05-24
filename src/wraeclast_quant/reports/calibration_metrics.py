from __future__ import annotations

from wraeclast_quant.reports.calibration_models import CalibrationResult, SCORE_BUCKETS
from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository


def build_calibration(
    repository: SnapshotRepository,
    limit: int = 20,
) -> CalibrationResult:
    reviews = repository.list_outcome_reviews(limit=None)
    recent_reviews = reviews[:limit]
    return CalibrationResult(
        reviews=reviews,
        recent_reviews=recent_reviews,
        by_action=_counts_by_action(reviews),
        by_score_bucket=_counts_by_score_bucket(reviews),
        average_score_by_outcome=_average_score_by_outcome(reviews),
    )


def score_bucket(score: float) -> str:
    if score >= 75.0:
        return "75+"
    if score >= 55.0:
        return "55-74.99"
    if score >= 35.0:
        return "35-54.99"
    return "<35"


def _counts_by_action(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for review in reviews:
        if review.action not in summary:
            summary[review.action] = _empty_outcome_counts()
        summary[review.action][review.outcome] += 1
    return summary


def _counts_by_score_bucket(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary = {bucket: _empty_outcome_counts() for bucket in SCORE_BUCKETS}
    for review in reviews:
        summary[score_bucket(review.opportunity_score)][review.outcome] += 1
    return summary


def _average_score_by_outcome(reviews: list[OutcomeReviewRecord]) -> dict[str, float | None]:
    scores = {outcome: [] for outcome in sorted(ALLOWED_OUTCOMES)}
    for review in reviews:
        scores[review.outcome].append(review.opportunity_score)
    return {
        outcome: (sum(values) / len(values) if values else None)
        for outcome, values in scores.items()
    }


def _empty_outcome_counts() -> dict[str, int]:
    return {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}
