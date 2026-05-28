from wraeclast_quant.reports.review_queue_commands import (
    batch_outcome_review_steps,
    record_outcome_command_templates,
)


def test_batch_outcome_review_steps_lists_review_files_and_dry_run() -> None:
    text = batch_outcome_review_steps(13)

    assert text == "\n".join(
        [
            "Batch review next steps:",
            "  wq review-queue --run-id 13 --output-path data/processed/review_queue.md",
            "  wq review-queue --run-id 13 --decisions-output-path data/processed/outcome_decisions_run_13.json",
            "  Fill outcome labels in data/processed/outcome_decisions_run_13.json.",
            "  wq record-outcomes --input-path data/processed/outcome_decisions_run_13.json --dry-run",
        ]
    )


def test_record_outcome_command_templates_escape_item_names() -> None:
    text = record_outcome_command_templates(
        13,
        ['Open ` "Catalyst"'],
    )

    assert text == "\n".join(
        [
            "Suggested review commands:",
            '  wq record-outcome --run-id 13 --item-name "Open `` `"Catalyst`"" --outcome positive|neutral|negative',
        ]
    )
