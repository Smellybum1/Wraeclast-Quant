from __future__ import annotations

from wraeclast_quant.reports.calibration_aggregates import (
    average_score_by_outcome,
    counts_by_action,
    counts_by_score_bucket,
)
from wraeclast_quant.reports.calibration_models import CalibrationResult
from wraeclast_quant.reports.calibration_score_buckets import score_bucket
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_calibration(
    repository: SnapshotRepository,
    limit: int = 20,
) -> CalibrationResult:
    reviews = repository.list_outcome_reviews(limit=None)
    recent_reviews = reviews[:limit]
    return CalibrationResult(
        reviews=reviews,
        recent_reviews=recent_reviews,
        by_action=counts_by_action(reviews),
        by_score_bucket=counts_by_score_bucket(reviews),
        average_score_by_outcome=average_score_by_outcome(reviews),
    )


__all__ = ["build_calibration", "score_bucket"]
