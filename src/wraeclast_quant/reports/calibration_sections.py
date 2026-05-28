from __future__ import annotations

from wraeclast_quant.reports.calibration_count_sections import (
    outcome_counts_by_action_section,
    outcome_counts_by_score_bucket_section,
)
from wraeclast_quant.reports.calibration_models import CalibrationResult
from wraeclast_quant.reports.calibration_review_prompts import (
    calibration_review_prompt_caveat,
    calibration_review_prompt_lines,
)
from wraeclast_quant.reports.outcome_markdown import reviewed_recommendation_row
from wraeclast_quant.reports.outcome_guidance import no_outcome_review_lines
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES


def calibration_report_header() -> list[str]:
    return [
        "# Wraeclast Quant Recommendation Calibration",
        "",
        "Local calibration artifact only. It summarizes manually recorded recommendation outcomes and does not change scoring weights or thresholds.",
        "",
    ]


def empty_calibration_report_body() -> list[str]:
    return no_outcome_review_lines()


def average_score_by_outcome_section(result: CalibrationResult) -> list[str]:
    lines = [
        "",
        "## Average Score By Outcome",
        "",
        "| Outcome | Average Score |",
        "| --- | ---: |",
    ]
    for outcome in sorted(ALLOWED_OUTCOMES):
        average = result.average_score_by_outcome[outcome]
        value = "" if average is None else f"{average:.2f}"
        lines.append(f"| {outcome} | {value} |")
    return lines


def calibration_review_prompts_section(result: CalibrationResult) -> list[str]:
    return [
        "",
        "## Calibration Review Prompts",
        "",
        calibration_review_prompt_caveat(),
        "",
        *calibration_review_prompt_lines(result),
    ]


def recent_reviewed_recommendations_section(result: CalibrationResult) -> list[str]:
    lines = [
        "",
        "## Recent Reviewed Recommendations",
        "",
        "| Run | Item | Score | Action | Outcome | Observed | Notes |",
        "| ---: | --- | ---: | --- | --- | --- | --- |",
    ]
    for review in result.recent_reviews:
        lines.append(reviewed_recommendation_row(review))
    lines.append("")
    return lines


__all__ = [
    "average_score_by_outcome_section",
    "calibration_report_header",
    "calibration_review_prompts_section",
    "empty_calibration_report_body",
    "outcome_counts_by_action_section",
    "outcome_counts_by_score_bucket_section",
    "recent_reviewed_recommendations_section",
]
