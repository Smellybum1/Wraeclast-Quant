from __future__ import annotations

from wraeclast_quant.storage.models import OutcomeReviewRecord


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def outcome_summary_row(label: str, counts: dict[str, int]) -> str:
    return (
        f"| {escape_cell(label)} | {counts.get('negative', 0)} | "
        f"{counts.get('neutral', 0)} | {counts.get('positive', 0)} |"
    )


def reviewed_recommendation_row(review: OutcomeReviewRecord) -> str:
    return (
        f"| {review.run_id} | {escape_cell(review.item_name)} | "
        f"{review.opportunity_score:.2f} | {escape_cell(review.action)} | "
        f"{review.outcome} | {escape_cell(review.observed_at)} | "
        f"{escape_cell(review.notes)} |"
    )


__all__ = ["escape_cell", "outcome_summary_row", "reviewed_recommendation_row"]
