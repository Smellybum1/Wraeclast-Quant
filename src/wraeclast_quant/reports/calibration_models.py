from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.storage.models import OutcomeReviewRecord

DEFAULT_CALIBRATION_REPORT_PATH = Path("data/processed/calibration_report.md")
SCORE_BUCKETS = ("75+", "55-74.99", "35-54.99", "<35")


@dataclass(frozen=True)
class CalibrationResult:
    reviews: list[OutcomeReviewRecord]
    recent_reviews: list[OutcomeReviewRecord]
    by_action: dict[str, dict[str, int]]
    by_score_bucket: dict[str, dict[str, int]]
    average_score_by_outcome: dict[str, float | None]

    @property
    def has_outcomes(self) -> bool:
        return bool(self.reviews)
