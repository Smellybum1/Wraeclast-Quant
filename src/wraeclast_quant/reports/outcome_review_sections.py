from __future__ import annotations

from wraeclast_quant.reports.outcome_markdown import (
    outcome_summary_row,
    reviewed_recommendation_row,
)
from wraeclast_quant.storage.models import OutcomeReviewRecord


def outcome_review_header() -> list[str]:
    return [
        "# Wraeclast Quant Outcome Review",
        "",
        "Local review artifact only. Outcome notes may contain user context and are not part of public intel exports.",
        "",
    ]


def empty_outcome_review_body() -> list[str]:
    return ["No reviewed recommendation outcomes found.", ""]


def outcome_summary_by_action_section(summary_by_action: dict[str, dict[str, int]]) -> list[str]:
    lines = [
        "## Outcome Summary By Action",
        "",
        "| Action | Negative | Neutral | Positive |",
        "| --- | ---: | ---: | ---: |",
    ]
    for action, counts in sorted(summary_by_action.items()):
        lines.append(outcome_summary_row(action, counts))
    return lines


def recent_reviewed_recommendations_section(
    reviews: list[OutcomeReviewRecord],
) -> list[str]:
    lines = [
        "",
        "## Recent Reviewed Recommendations",
        "",
        "| Run | Item | Score | Action | Outcome | Observed | Notes |",
        "| ---: | --- | ---: | --- | --- | --- | --- |",
    ]
    for review in reviews:
        lines.append(reviewed_recommendation_row(review))
    lines.append("")
    return lines


__all__ = [
    "empty_outcome_review_body",
    "outcome_review_header",
    "outcome_summary_by_action_section",
    "recent_reviewed_recommendations_section",
]
