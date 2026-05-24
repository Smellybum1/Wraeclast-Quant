from __future__ import annotations

from wraeclast_quant.reports.calibration_models import CalibrationResult, SCORE_BUCKETS
from wraeclast_quant.reports.outcome_markdown import outcome_summary_row


def outcome_counts_by_action_section(result: CalibrationResult) -> list[str]:
    lines = [
        "## Outcome Counts By Action",
        "",
        "| Action | Negative | Neutral | Positive |",
        "| --- | ---: | ---: | ---: |",
    ]
    for action, counts in sorted(result.by_action.items()):
        lines.append(outcome_summary_row(action, counts))
    return lines


def outcome_counts_by_score_bucket_section(result: CalibrationResult) -> list[str]:
    lines = [
        "",
        "## Outcome Counts By Score Bucket",
        "",
        "| Score Bucket | Negative | Neutral | Positive |",
        "| --- | ---: | ---: | ---: |",
    ]
    for bucket in SCORE_BUCKETS:
        lines.append(outcome_summary_row(bucket, result.by_score_bucket[bucket]))
    return lines


__all__ = [
    "outcome_counts_by_action_section",
    "outcome_counts_by_score_bucket_section",
]
