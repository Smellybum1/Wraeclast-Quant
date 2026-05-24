from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.outcome_review_sections import (
    empty_outcome_review_body,
    outcome_review_header,
    outcome_summary_by_action_section,
    recent_reviewed_recommendations_section,
)
from wraeclast_quant.storage.models import OutcomeReviewRecord

DEFAULT_OUTCOME_REVIEW_PATH = Path("data/processed/outcome_review.md")


def render_outcome_review(
    reviews: list[OutcomeReviewRecord],
    summary_by_action: dict[str, dict[str, int]],
) -> str:
    lines = outcome_review_header()
    if not reviews:
        lines.extend(empty_outcome_review_body())
        return "\n".join(lines)

    lines.extend(outcome_summary_by_action_section(summary_by_action))
    lines.extend(recent_reviewed_recommendations_section(reviews))
    return "\n".join(lines)


def write_outcome_review(
    reviews: list[OutcomeReviewRecord],
    summary_by_action: dict[str, dict[str, int]],
    path: Path = DEFAULT_OUTCOME_REVIEW_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_outcome_review(reviews, summary_by_action),
        encoding="utf-8",
    )
    return path
