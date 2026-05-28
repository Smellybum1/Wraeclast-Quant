from pathlib import Path

from wraeclast_quant.reports.calibration import render_calibration_report
from wraeclast_quant.reports.outcome_review import render_outcome_review
from wraeclast_quant.reports.review_queue_worksheet import render_review_queue_worksheet
from wraeclast_quant.storage.models import StoredOpportunityRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

from outcome_review_helpers import build_calibration_from_reviews
from outcome_review_helpers import documented_bullets as _documented_bullets
from outcome_review_helpers import review_record as _review


def test_outcome_contract_doc_matches_allowed_outcomes_and_report_markers() -> None:
    doc_text = Path("docs/OUTCOMES.md").read_text(encoding="utf-8")
    documented_outcomes = _documented_bullets(doc_text, "Allowed outcome labels:")
    documented_markers = _documented_bullets(doc_text, "The local outcome review report includes:")
    documented_calibration_markers = _documented_bullets(doc_text, "The local calibration report includes:")
    documented_worksheet_markers = _documented_bullets(doc_text, "The local review queue worksheet includes:")
    report = render_outcome_review(
        reviews=[_review()],
        summary_by_action={"BUY": {"negative": 0, "neutral": 0, "positive": 1}},
    )
    calibration_report = render_calibration_report(build_calibration_from_reviews([_review()]))
    worksheet = render_review_queue_worksheet(
        7,
        "sample-data",
        [
            StoredOpportunityRecord(
                id=1,
                run_id=7,
                item_name="Stormglass Catalyst",
                opportunity_score=76.0,
                action="BUY",
                inputs={},
            )
        ],
    )

    assert documented_outcomes == ALLOWED_OUTCOMES
    for marker in documented_markers:
        assert marker in report
    for marker in documented_calibration_markers:
        assert marker in calibration_report
    for marker in documented_worksheet_markers:
        assert marker in worksheet
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md" in doc_text
    assert "wq review-queue --output-path data/processed/review_queue.md" not in doc_text
    assert "Fully reviewed runs with calibration review prompts point back to `wq calibration`." in doc_text
    assert "When calibration review prompts exist, it surfaces the local read-only prompt count." in doc_text
    assert "After successful writes, active calibration review prompts surface" in doc_text
    assert "After a successful final write, active calibration review prompts surface" in doc_text
    assert "No reviewed recommendation outcomes found." in render_outcome_review([], {})
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md" in render_outcome_review(
        [],
        {},
    )
    assert "wq record-outcomes --input-path data/processed/outcome_decisions_run_<id>.json --dry-run" in render_outcome_review(
        [],
        {},
    )
    assert "data/processed/review_queue_run_<id>.md" in render_outcome_review([], {})
    assert "positive=useful signal" in render_calibration_report(build_calibration_from_reviews([]))
