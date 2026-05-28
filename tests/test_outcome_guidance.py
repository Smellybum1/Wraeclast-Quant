from wraeclast_quant.reports.outcome_guidance import (
    LOCAL_REPORT_NEXT_ACTION,
    local_report_next_action,
    no_outcome_review_lines,
)


def test_local_report_next_action_mentions_local_handoff_checks() -> None:
    assert local_report_next_action() == LOCAL_REPORT_NEXT_ACTION
    assert "Local report artifact only." in local_report_next_action()
    assert "wq status --strict and wq publish-check" in local_report_next_action()


def test_no_outcome_review_lines_include_batch_review_flow() -> None:
    text = "\n".join(no_outcome_review_lines())

    assert "No reviewed recommendation outcomes found." in text
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md" in text
    assert "wq record-outcomes --input-path data/processed/outcome_decisions_run_<id>.json" in text
    assert "positive=useful signal" in text
