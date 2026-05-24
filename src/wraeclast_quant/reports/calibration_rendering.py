from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.calibration_models import (
    DEFAULT_CALIBRATION_REPORT_PATH,
    CalibrationResult,
    SCORE_BUCKETS,
)
from wraeclast_quant.reports.outcome_markdown import (
    outcome_summary_row,
    reviewed_recommendation_row,
)
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES


def render_calibration_report(result: CalibrationResult) -> str:
    lines = [
        "# Wraeclast Quant Recommendation Calibration",
        "",
        "Local calibration artifact only. It summarizes manually recorded recommendation outcomes and does not change scoring weights or thresholds.",
        "",
    ]
    if not result.has_outcomes:
        lines.extend(["No reviewed recommendation outcomes found.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "## Outcome Counts By Action",
            "",
            "| Action | Negative | Neutral | Positive |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for action, counts in sorted(result.by_action.items()):
        lines.append(outcome_summary_row(action, counts))

    lines.extend(
        [
            "",
            "## Outcome Counts By Score Bucket",
            "",
            "| Score Bucket | Negative | Neutral | Positive |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for bucket in SCORE_BUCKETS:
        lines.append(outcome_summary_row(bucket, result.by_score_bucket[bucket]))

    lines.extend(
        [
            "",
            "## Average Score By Outcome",
            "",
            "| Outcome | Average Score |",
            "| --- | ---: |",
        ]
    )
    for outcome in sorted(ALLOWED_OUTCOMES):
        average = result.average_score_by_outcome[outcome]
        value = "" if average is None else f"{average:.2f}"
        lines.append(f"| {outcome} | {value} |")

    lines.extend(["", "## Recent Reviewed Recommendations", ""])
    lines.extend(
        [
            "| Run | Item | Score | Action | Outcome | Observed | Notes |",
            "| ---: | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for review in result.recent_reviews:
        lines.append(reviewed_recommendation_row(review))
    lines.append("")
    return "\n".join(lines)


def write_calibration_report(
    result: CalibrationResult,
    path: Path = DEFAULT_CALIBRATION_REPORT_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_calibration_report(result), encoding="utf-8")
    return path
