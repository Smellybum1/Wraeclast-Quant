from __future__ import annotations

from wraeclast_quant.reports.calibration import build_calibration
from wraeclast_quant.storage.models import OutcomeReviewRecord


def review_record(
    id: int = 1,
    item_name: str = "Stormglass Catalyst",
    action: str = "BUY",
    outcome: str = "positive",
    notes: str = "",
    score: float = 76.0,
) -> OutcomeReviewRecord:
    return OutcomeReviewRecord(
        id=id,
        run_id=7,
        item_name=item_name,
        outcome=outcome,
        notes=notes,
        observed_at="2026-05-23T00:00:00+00:00",
        opportunity_score=score,
        action=action,
    )


def build_calibration_from_reviews(
    reviews: list[OutcomeReviewRecord],
    limit: int = 20,
):
    class FakeRepository:
        def list_outcome_reviews(self, limit=None):
            if limit is None:
                return reviews
            return reviews[:limit]

    return build_calibration(FakeRepository(), limit=limit)  # type: ignore[arg-type]


def documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }


__all__ = [
    "build_calibration_from_reviews",
    "documented_bullets",
    "review_record",
]
