from __future__ import annotations


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


def review_queue_worksheet_command(run_id: int) -> str:
    return (
        f"wq review-queue --run-id {run_id} "
        "--output-path data/processed/review_queue.md"
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
    "local_review_caveat",
    "outcome_label_guide",
    "powershell_double_quoted_text",
    "record_outcome_command",
    "review_queue_worksheet_command",
]
