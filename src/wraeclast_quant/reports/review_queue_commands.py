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


def _database_path_option(database_path: object | None) -> str:
    if database_path is None:
        return ""
    return f"--database-path {database_path} "


def review_queue_worksheet_command(
    run_id: int | str,
    *,
    database_path: object | None = None,
) -> str:
    worksheet_path = run_review_queue_worksheet_path(run_id)
    return (
        f"wq review-queue {_database_path_option(database_path)}--run-id {run_id} "
        f"--output-path {worksheet_path}"
    )


def review_queue_decisions_template_command(
    run_id: int | str,
    *,
    database_path: object | None = None,
) -> str:
    decisions_path = run_outcome_decisions_path(run_id)
    return (
        f"wq review-queue {_database_path_option(database_path)}--run-id {run_id} "
        f"--decisions-output-path {decisions_path}"
    )


def record_outcomes_dry_run_command(
    input_path: str = OUTCOME_DECISIONS_PATH,
    *,
    database_path: object | None = None,
) -> str:
    return f"{record_outcomes_command(input_path, database_path=database_path)} --dry-run"


def record_outcomes_command(
    input_path: str = OUTCOME_DECISIONS_PATH,
    *,
    database_path: object | None = None,
) -> str:
    return f"wq record-outcomes {_database_path_option(database_path)}--input-path {input_path}"


def batch_outcome_review_next_action(
    run_id: int | str,
    *,
    database_path: object | None = None,
) -> str:
    decisions_path = run_outcome_decisions_path(run_id)
    return (
        f"{review_queue_worksheet_command(run_id, database_path=database_path)}; "
        f"{review_queue_decisions_template_command(run_id, database_path=database_path)}; "
        "fill outcomes; "
        f"{record_outcomes_dry_run_command(decisions_path, database_path=database_path)}"
    )


def batch_outcome_review_steps(
    run_id: int | str,
    *,
    database_path: object | None = None,
) -> str:
    decisions_path = run_outcome_decisions_path(run_id)
    return "\n".join(
        [
            "Batch review next steps:",
            f"  {review_queue_worksheet_command(run_id, database_path=database_path)}",
            f"  {review_queue_decisions_template_command(run_id, database_path=database_path)}",
            f"  Fill outcome labels in {decisions_path}.",
            f"  {record_outcomes_dry_run_command(decisions_path, database_path=database_path)}",
        ]
    )


def review_coverage_command(run_id: int | str) -> str:
    return f"wq review-coverage --run-id {run_id}"


def status_outcome_review_next_action(run_id: int | str) -> str:
    return (
        f"{review_coverage_command(run_id)} for worksheet, "
        "outcome-decisions, and dry-run steps"
    )


def run_outcome_decisions_path(run_id: int | str) -> str:
    return f"data/processed/outcome_decisions_run_{run_id}.json"


def run_review_queue_worksheet_path(run_id: int | str) -> str:
    return f"data/processed/review_queue_run_{run_id}.md"


def record_outcome_command(
    run_id: int,
    item_name: str,
    *,
    outcome: str = "positive|neutral|negative",
    database_path: object | None = None,
) -> str:
    return (
        f"wq record-outcome {_database_path_option(database_path)}"
        f"--run-id {run_id} "
        f'--item-name "{powershell_double_quoted_text(item_name)}" '
        f"--outcome {outcome}"
    )


def record_outcome_command_templates(
    run_id: int,
    item_names: list[str],
    *,
    database_path: object | None = None,
) -> str:
    lines = ["Suggested review commands:"]
    for item_name in item_names:
        lines.append(
            f"  {record_outcome_command(run_id, item_name, database_path=database_path)}"
        )
    return "\n".join(lines)


def powershell_double_quoted_text(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')


__all__ = [
    "OUTCOME_DECISIONS_PATH",
    "batch_outcome_review_steps",
    "batch_outcome_review_next_action",
    "local_review_caveat",
    "outcome_label_guide",
    "powershell_double_quoted_text",
    "record_outcome_command_templates",
    "record_outcomes_command",
    "record_outcomes_dry_run_command",
    "record_outcome_command",
    "review_coverage_command",
    "review_queue_decisions_template_command",
    "review_queue_worksheet_command",
    "run_outcome_decisions_path",
    "run_review_queue_worksheet_path",
    "status_outcome_review_next_action",
]
