from wraeclast_quant.reports.calibration import (
    calibration_review_prompts,
    render_calibration_report,
)

from outcome_review_helpers import build_calibration_from_reviews
from outcome_review_helpers import review_record as _review


def test_calibration_review_prompts_flag_avoid_positive_and_low_positive_average() -> None:
    result = build_calibration_from_reviews(
        [
            _review(item_name="Avoid Good", action="AVOID", outcome="positive", score=20.0),
            _review(item_name="Watch Mixed", action="WATCH", outcome="neutral", score=60.0),
        ]
    )

    prompts = calibration_review_prompts(result)

    assert prompts == [
        "AVOID has 1 positive outcome(s); inspect low-score signal coverage before changing scoring.",
        "Positive outcomes average 20.00, below neutral average 60.00; review score buckets before tuning thresholds.",
    ]


def test_calibration_review_prompts_flag_higher_action_negative() -> None:
    result = build_calibration_from_reviews(
        [
            _review(item_name="Watch Bad", action="WATCH", outcome="negative", score=60.0),
        ]
    )

    assert calibration_review_prompts(result) == [
        "WATCH has 1 negative outcome(s); inspect stale inputs or threshold behavior before changing scoring.",
    ]


def test_calibration_report_renders_review_prompt_section_without_retuning() -> None:
    report = render_calibration_report(
        build_calibration_from_reviews(
            [
                _review(item_name="Avoid Good", action="AVOID", outcome="positive", score=20.0),
            ]
        )
    )

    assert "## Calibration Review Prompts" in report
    assert "Review prompts are local-only and read-only." in report
    assert "They do not retune scoring or change recommendations." in report
    assert "AVOID has 1 positive outcome(s)" in report


def test_calibration_report_renders_empty_review_prompt_state() -> None:
    report = render_calibration_report(build_calibration_from_reviews([_review()]))

    assert "## Calibration Review Prompts" in report
    assert "No calibration review prompts triggered." in report
