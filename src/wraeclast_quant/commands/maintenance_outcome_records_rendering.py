from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.review_queue_commands import record_outcomes_command
from wraeclast_quant.storage.models import RecommendationOutcomeRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

console = Console(width=260)


def post_outcome_record_next_steps(run_id: int) -> str:
    return (
        f"Next: wq review-coverage --run-id {run_id}; "
        "then wq outcomes, wq outcome-review, and wq calibration for local feedback. "
        "Run wq export, wq site, and wq site-bundle when you want derived artifacts refreshed."
    )


def batch_outcome_dry_run_success_message(
    decision_count: int,
    run_id: int,
    input_path: object,
) -> str:
    return "\n".join(
        [
            f"Validated {decision_count} outcome decision(s) for run #{run_id} "
            f"from {input_path}; no records written.",
            f"Next: {record_outcomes_command(str(input_path))}",
        ]
    )


def batch_outcome_record_success_message(
    record_count: int,
    run_id: int,
    input_path: object,
) -> str:
    return f"Recorded {record_count} outcome(s) for run #{run_id} from {input_path}."


def batch_outcome_write_error_message(error: BaseException) -> str:
    return f"Error: could not record outcome batch; no records written: {error}"


def recent_outcomes_next_action() -> str:
    return (
        "Next: run wq outcome-review to inspect scores/actions with outcomes, "
        "or wq calibration to summarize reviewed recommendations."
    )


def no_outcomes_message() -> str:
    return "No recommendation outcomes recorded."


def print_outcome_record(record: RecommendationOutcomeRecord) -> None:
    console.print(f"Recorded {record.outcome} outcome for '{record.item_name}' from run #{record.run_id}.")
    console.print(post_outcome_record_next_steps(record.run_id))


def print_recent_outcomes(
    records: list[RecommendationOutcomeRecord],
    summary: dict[str, int],
) -> None:
    table = Table(title="Recommendation Outcomes")
    table.add_column("Run", justify="right")
    table.add_column("Item")
    table.add_column("Outcome")
    table.add_column("Observed")
    table.add_column("Notes")
    for record in records:
        table.add_row(
            str(record.run_id),
            record.item_name,
            record.outcome,
            record.observed_at,
            record.notes,
        )
    console.print(table)

    summary_table = Table(title="Outcome Summary")
    summary_table.add_column("Outcome")
    summary_table.add_column("Count", justify="right")
    for label in sorted(ALLOWED_OUTCOMES):
        summary_table.add_row(label, str(summary.get(label, 0)))
    console.print(summary_table)
    console.print(recent_outcomes_next_action())


def print_no_outcomes() -> None:
    console.print(no_outcomes_message())


__all__ = [
    "batch_outcome_dry_run_success_message",
    "batch_outcome_record_success_message",
    "batch_outcome_write_error_message",
    "no_outcomes_message",
    "post_outcome_record_next_steps",
    "print_no_outcomes",
    "print_outcome_record",
    "print_recent_outcomes",
    "recent_outcomes_next_action",
]
