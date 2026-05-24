from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.calibration import CalibrationResult, SCORE_BUCKETS
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

console = Console(width=260)


def print_calibration_tables(result: CalibrationResult) -> None:
    by_action = Table(title="Calibration By Action")
    by_action.add_column("Action")
    for label in sorted(ALLOWED_OUTCOMES):
        by_action.add_column(label, justify="right")
    for action, counts in sorted(result.by_action.items()):
        by_action.add_row(
            action,
            *(str(counts.get(label, 0)) for label in sorted(ALLOWED_OUTCOMES)),
        )
    console.print(by_action)

    by_bucket = Table(title="Calibration By Score Bucket")
    by_bucket.add_column("Score Bucket")
    for label in sorted(ALLOWED_OUTCOMES):
        by_bucket.add_column(label, justify="right")
    for bucket in SCORE_BUCKETS:
        counts = result.by_score_bucket[bucket]
        by_bucket.add_row(
            bucket,
            *(str(counts.get(label, 0)) for label in sorted(ALLOWED_OUTCOMES)),
        )
    console.print(by_bucket)

    averages = Table(title="Average Score By Outcome")
    averages.add_column("Outcome")
    averages.add_column("Average Score", justify="right")
    for outcome in sorted(ALLOWED_OUTCOMES):
        average = result.average_score_by_outcome[outcome]
        averages.add_row(outcome, "" if average is None else f"{average:.2f}")
    console.print(averages)

    recent = Table(title="Recent Reviewed Recommendations")
    recent.add_column("Run", justify="right")
    recent.add_column("Item")
    recent.add_column("Score", justify="right")
    recent.add_column("Action")
    recent.add_column("Outcome")
    recent.add_column("Observed")
    for review in result.recent_reviews:
        recent.add_row(
            str(review.run_id),
            review.item_name,
            f"{review.opportunity_score:.2f}",
            review.action,
            review.outcome,
            review.observed_at,
        )
    console.print(recent)
