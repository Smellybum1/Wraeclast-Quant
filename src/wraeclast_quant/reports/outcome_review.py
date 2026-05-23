from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

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
        lines.append(
            f"| {_escape_cell(action)} | {counts.get('negative', 0)} | "
            f"{counts.get('neutral', 0)} | {counts.get('positive', 0)} |"
        )
    lines.extend(["", "## Recent Reviewed Recommendations", ""])
    lines.extend(
        [
            "| Run | Item | Score | Action | Outcome | Observed | Notes |",
            "| ---: | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for review in reviews:
        lines.append(
            f"| {review.run_id} | {_escape_cell(review.item_name)} | "
            f"{review.opportunity_score:.2f} | {_escape_cell(review.action)} | "
            f"{review.outcome} | {_escape_cell(review.observed_at)} | "
            f"{_escape_cell(review.notes)} |"
        )
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


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
