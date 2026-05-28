from wraeclast_quant.commands.intake_watchlist_rendering import (
    calibration_prompt_next_action,
)
from wraeclast_quant.reports.review_guidance import manual_review_handoff_next_action


def test_calibration_prompt_next_action_is_read_only() -> None:
    assert calibration_prompt_next_action(2) == (
        "Calibration prompts: 2 local read-only prompt(s). "
        "Next: wq calibration. Prompts do not retune scoring or change recommendations."
    )


def test_manual_review_handoff_next_action_prioritizes_unreviewed_items() -> None:
    assert manual_review_handoff_next_action(
        run_id=13,
        unreviewed_recommendations=1,
        calibration_prompt_count=2,
    ) == (
        "Next: wq review-queue --run-id 13 --output-path data/processed/review_queue.md; "
        "wq review-queue --run-id 13 --decisions-output-path data/processed/outcome_decisions.json; "
        "fill outcomes; wq record-outcomes --input-path data/processed/outcome_decisions.json --dry-run"
    )
