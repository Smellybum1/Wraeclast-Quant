from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.calibration_models import (
    DEFAULT_CALIBRATION_REPORT_PATH,
    CalibrationResult,
)
from wraeclast_quant.reports.calibration_sections import (
    average_score_by_outcome_section,
    calibration_report_header,
    empty_calibration_report_body,
    outcome_counts_by_action_section,
    outcome_counts_by_score_bucket_section,
    recent_reviewed_recommendations_section,
)


def render_calibration_report(result: CalibrationResult) -> str:
    lines = calibration_report_header()
    if not result.has_outcomes:
        lines.extend(empty_calibration_report_body())
        return "\n".join(lines)

    lines.extend(outcome_counts_by_action_section(result))
    lines.extend(outcome_counts_by_score_bucket_section(result))
    lines.extend(average_score_by_outcome_section(result))
    lines.extend(recent_reviewed_recommendations_section(result))
    return "\n".join(lines)


def write_calibration_report(
    result: CalibrationResult,
    path: Path = DEFAULT_CALIBRATION_REPORT_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_calibration_report(result), encoding="utf-8")
    return path
