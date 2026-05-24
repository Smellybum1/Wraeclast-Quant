from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.outcome_markdown import (
    outcome_summary_row,
    reviewed_recommendation_row,
)
from wraeclast_quant.storage.models import OutcomeReviewRecord

DEFAULT_OUTCOME_REVIEW_PATH = Path("data/processed/outcome_review.md")


def render_outcome_review(
    reviews: list[OutcomeReviewRecord],
    summary_by_action: dict[str, dict[str, int]],
) -> str:
    lines = [
        "# Wraeclast Quant Outcome Review",
        "",
        "Local review artifact only. Outcome notes may contain user context and are not part of public intel exports.",
        "",
    ]
    if not reviews:
        lines.extend(["No reviewed recommendation outcomes found.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "## Outcome Summary By Action",
            "",
            "| Action | Negative | Neutral | Positive |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for action, counts in sorted(summary_by_action.items()):
        lines.append(outcome_summary_row(action, counts))
    lines.extend(["", "## Recent Reviewed Recommendations", ""])
    lines.extend(
        [
            "| Run | Item | Score | Action | Outcome | Observed | Notes |",
            "| ---: | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for review in reviews:
        lines.append(reviewed_recommendation_row(review))
    lines.append("")
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
