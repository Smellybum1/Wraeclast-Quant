from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository

DEFAULT_CALIBRATION_REPORT_PATH = Path("data/processed/calibration_report.md")
SCORE_BUCKETS = ("75+", "55-74.99", "35-54.99", "<35")


@dataclass(frozen=True)
class CalibrationResult:
    reviews: list[OutcomeReviewRecord]
    recent_reviews: list[OutcomeReviewRecord]
    by_action: dict[str, dict[str, int]]
    by_score_bucket: dict[str, dict[str, int]]
    average_score_by_outcome: dict[str, float | None]

    @property
    def has_outcomes(self) -> bool:
        return bool(self.reviews)


def build_calibration(
    repository: SnapshotRepository,
    limit: int = 20,
) -> CalibrationResult:
    reviews = repository.list_outcome_reviews(limit=None)
    recent_reviews = reviews[:limit]
    return CalibrationResult(
        reviews=reviews,
        recent_reviews=recent_reviews,
        by_action=_counts_by_action(reviews),
        by_score_bucket=_counts_by_score_bucket(reviews),
        average_score_by_outcome=_average_score_by_outcome(reviews),
    )


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
        lines.append(_summary_row(action, counts))

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
        lines.append(_summary_row(bucket, result.by_score_bucket[bucket]))

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
        lines.append(
            f"| {review.run_id} | {_escape_cell(review.item_name)} | "
            f"{review.opportunity_score:.2f} | {_escape_cell(review.action)} | "
            f"{review.outcome} | {_escape_cell(review.observed_at)} | "
            f"{_escape_cell(review.notes)} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_calibration_report(
    result: CalibrationResult,
    path: Path = DEFAULT_CALIBRATION_REPORT_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_calibration_report(result), encoding="utf-8")
    return path


def score_bucket(score: float) -> str:
    if score >= 75.0:
        return "75+"
    if score >= 55.0:
        return "55-74.99"
    if score >= 35.0:
        return "35-54.99"
    return "<35"


def _counts_by_action(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for review in reviews:
        if review.action not in summary:
            summary[review.action] = _empty_outcome_counts()
        summary[review.action][review.outcome] += 1
    return summary


def _counts_by_score_bucket(reviews: list[OutcomeReviewRecord]) -> dict[str, dict[str, int]]:
    summary = {bucket: _empty_outcome_counts() for bucket in SCORE_BUCKETS}
    for review in reviews:
        summary[score_bucket(review.opportunity_score)][review.outcome] += 1
    return summary


def _average_score_by_outcome(reviews: list[OutcomeReviewRecord]) -> dict[str, float | None]:
    scores = {outcome: [] for outcome in sorted(ALLOWED_OUTCOMES)}
    for review in reviews:
        scores[review.outcome].append(review.opportunity_score)
    return {
        outcome: (sum(values) / len(values) if values else None)
        for outcome, values in scores.items()
    }


def _empty_outcome_counts() -> dict[str, int]:
    return {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}


def _summary_row(label: str, counts: dict[str, int]) -> str:
    return (
        f"| {_escape_cell(label)} | {counts.get('negative', 0)} | "
        f"{counts.get('neutral', 0)} | {counts.get('positive', 0)} |"
    )


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
