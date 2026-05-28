from pathlib import Path

from wraeclast_quant.commands.maintenance_outcome_reports_rendering import (
    outcome_review_next_action,
    outcome_report_written_message,
)


def test_outcome_report_written_message_for_reviewed_report() -> None:
    path = Path("outcome_review.md")

    assert (
        outcome_report_written_message(path, has_reviews=True)
        == f"Wrote outcome review report to {path}"
    )


def test_outcome_report_written_message_for_empty_report() -> None:
    path = Path("outcome_review.md")

    assert (
        outcome_report_written_message(path, has_reviews=False)
        == f"Wrote empty outcome review report to {path}"
    )


def test_outcome_review_next_action_preserves_cli_text() -> None:
    assert outcome_review_next_action() == (
        "Next: run wq calibration for read-only score/action summaries, "
        "or wq outcome-report --output-path data/processed/outcome_review.md "
        "to write a local Markdown report."
    )
