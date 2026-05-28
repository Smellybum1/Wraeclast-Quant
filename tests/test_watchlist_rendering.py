from wraeclast_quant.commands.intake_watchlist_rendering import (
    calibration_prompt_next_action,
    hidden_watchlist_items_text,
)
from wraeclast_quant.reports.review_guidance import manual_review_handoff_next_action


def test_calibration_prompt_next_action_is_read_only() -> None:
    assert calibration_prompt_next_action(2) == (
        "Calibration prompts: 2 local read-only prompt(s). "
        "Next: wq calibration. Prompts do not retune scoring or change recommendations."
    )


def test_hidden_watchlist_items_text_points_to_limit_for_truncated_runs() -> None:
    assert hidden_watchlist_items_text(displayed_count=5, total_count=6) == (
        "Showing top 5 of 6 scored opportunities. Re-run with --limit 6 to show all."
    )
    assert hidden_watchlist_items_text(displayed_count=5, total_count=80) == (
        "Showing top 5 of 80 scored opportunities. Re-run with --limit 50 to show more."
    )
    assert hidden_watchlist_items_text(displayed_count=6, total_count=6) is None


def test_manual_review_handoff_next_action_prioritizes_unreviewed_items() -> None:
    assert manual_review_handoff_next_action(
        run_id=13,
        unreviewed_recommendations=1,
        calibration_prompt_count=2,
    ) == (
        "Next: wq review-queue --run-id 13 --output-path data/processed/review_queue_run_13.md; "
        "wq review-queue --run-id 13 --decisions-output-path data/processed/outcome_decisions_run_13.json; "
        "fill outcomes; wq record-outcomes --input-path data/processed/outcome_decisions_run_13.json --dry-run"
    )
