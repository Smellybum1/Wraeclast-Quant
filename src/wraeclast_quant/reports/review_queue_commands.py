from __future__ import annotations


OUTCOME_DECISIONS_PATH = "data/processed/outcome_decisions.json"


def local_review_caveat(source_mode: str) -> str:
    return (
        f"Run source: {source_mode}. Review outcomes are local decision-support only; "
        "no trades, whispers, gameplay, publishing, or live collection are performed."
    )


def outcome_label_guide() -> str:
    return (
        "Outcome labels: positive=useful signal, neutral=mixed or unclear, "
        "negative=not useful after review."
    )


def review_queue_worksheet_command(run_id: int | str) -> str:
    return (
        f"wq review-queue --run-id {run_id} "
        "--output-path data/processed/review_queue.md"
    )


def review_queue_decisions_template_command(run_id: int | str) -> str:
    return (
        f"wq review-queue --run-id {run_id} "
        f"--decisions-output-path {OUTCOME_DECISIONS_PATH}"
    )


def record_outcomes_dry_run_command(input_path: str = OUTCOME_DECISIONS_PATH) -> str:
    return f"{record_outcomes_command(input_path)} --dry-run"


def record_outcomes_command(input_path: str = OUTCOME_DECISIONS_PATH) -> str:
    return f"wq record-outcomes --input-path {input_path}"


def batch_outcome_review_next_action(run_id: int | str) -> str:
    return (
        f"{review_queue_worksheet_command(run_id)}; "
        f"{review_queue_decisions_template_command(run_id)}; "
        f"fill outcomes; {record_outcomes_dry_run_command()}"
    )


def review_coverage_command(run_id: int | str) -> str:
    return f"wq review-coverage --run-id {run_id}"


def status_outcome_review_next_action(run_id: int | str) -> str:
    return (
        f"{review_coverage_command(run_id)} for worksheet, "
        "outcome-decisions, and dry-run steps"
    )


def record_outcome_command(
    run_id: int,
    item_name: str,
    *,
    outcome: str = "positive|neutral|negative",
) -> str:
    return (
        "wq record-outcome "
        f"--run-id {run_id} "
        f'--item-name "{powershell_double_quoted_text(item_name)}" '
        f"--outcome {outcome}"
    )


def powershell_double_quoted_text(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')


__all__ = [
    "OUTCOME_DECISIONS_PATH",
    "batch_outcome_review_next_action",
    "local_review_caveat",
    "outcome_label_guide",
    "powershell_double_quoted_text",
    "record_outcomes_command",
    "record_outcomes_dry_run_command",
    "record_outcome_command",
    "review_coverage_command",
    "review_queue_decisions_template_command",
    "review_queue_worksheet_command",
    "status_outcome_review_next_action",
]
