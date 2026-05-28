from __future__ import annotations

from wraeclast_quant.reports.review_queue_commands import batch_outcome_review_next_action
from wraeclast_quant.storage.models import ReviewCoverageRecord


def review_next_action(run_id: int, coverage: ReviewCoverageRecord) -> str:
    reviewed = f"{coverage.reviewed_recommendations}/{coverage.total_recommendations} reviewed"
    if coverage.unreviewed_recommendations:
        return (
            f"Review coverage: {reviewed}; {coverage.unreviewed_recommendations} unreviewed. "
            f"Next: {batch_outcome_review_next_action(run_id)}."
        )
    return f"Review coverage: {reviewed}; all recommendations for run #{run_id} have outcomes."


def calibration_prompt_next_action(prompt_count: int) -> str:
    return (
        f"Calibration prompts: {prompt_count} local read-only prompt(s). "
        "Next: wq calibration. Prompts do not retune scoring or change recommendations."
    )


def manual_review_handoff_next_action(
    *,
    run_id: int,
    unreviewed_recommendations: int,
    calibration_prompt_count: int = 0,
) -> str:
    if unreviewed_recommendations:
        return f"Next: {batch_outcome_review_next_action(run_id)}"
    if calibration_prompt_count:
        return calibration_prompt_next_action(calibration_prompt_count)
    return f"Next: All recommendations for run #{run_id} have outcomes."


__all__ = [
    "calibration_prompt_next_action",
    "manual_review_handoff_next_action",
    "review_next_action",
]
