from pathlib import Path

from wraeclast_quant.reports.calibration import (
    render_calibration_report,
)
from wraeclast_quant.reports.outcome_review import render_outcome_review, write_outcome_review
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

from outcome_review_helpers import build_calibration_from_reviews
from outcome_review_helpers import documented_bullets as _documented_bullets
from outcome_review_helpers import review_record as _review


def test_outcome_review_report_renders_summary_and_recent_reviews() -> None:
    report = render_outcome_review(
        reviews=[
            _review(
                item_name="Stormglass Catalyst",
                action="BUY",
                outcome="positive",
                notes="Good follow-through.",
            )
        ],
        summary_by_action={"BUY": {"negative": 0, "neutral": 0, "positive": 1}},
    )

    assert "# Wraeclast Quant Outcome Review" in report
    assert "## Outcome Summary By Action" in report
    assert "| BUY | 0 | 0 | 1 |" in report
    assert "## Recent Reviewed Recommendations" in report
    assert "| 7 | Stormglass Catalyst | 76.00 | BUY | positive |" in report
    assert "Good follow-through." in report


def test_outcome_review_report_renders_empty_message() -> None:
    report = render_outcome_review([], {})

    assert "No reviewed recommendation outcomes found." in report
    assert "Recent Reviewed Recommendations" not in report


def test_outcome_review_report_escapes_markdown_table_cells() -> None:
    report = render_outcome_review(
        reviews=[
            _review(
                item_name="Catalyst | Split",
                notes="Line one\nLine two | pipe",
            )
        ],
        summary_by_action={"BUY | WATCH": {"negative": 0, "neutral": 1, "positive": 0}},
    )

    assert "Catalyst \\| Split" in report
    assert "Line one Line two \\| pipe" in report
    assert "BUY \\| WATCH" in report


def test_write_outcome_review_creates_parent_directory(tmp_path: Path) -> None:
    output_path = write_outcome_review(
        reviews=[_review()],
        summary_by_action={"BUY": {"negative": 0, "neutral": 0, "positive": 1}},
        path=tmp_path / "reports" / "outcome_review.md",
    )

    assert output_path.exists()
    assert "Wraeclast Quant Outcome Review" in output_path.read_text(encoding="utf-8")


def test_outcome_contract_doc_matches_allowed_outcomes_and_report_markers() -> None:
    doc_text = Path("docs/OUTCOMES.md").read_text(encoding="utf-8")
    documented_outcomes = _documented_bullets(doc_text, "Allowed outcome labels:")
    documented_markers = _documented_bullets(doc_text, "The local outcome review report includes:")
    documented_calibration_markers = _documented_bullets(doc_text, "The local calibration report includes:")
    report = render_outcome_review(
        reviews=[_review()],
        summary_by_action={"BUY": {"negative": 0, "neutral": 0, "positive": 1}},
    )
    calibration_report = render_calibration_report(build_calibration_from_reviews([_review()]))

    assert documented_outcomes == ALLOWED_OUTCOMES
    for marker in documented_markers:
        assert marker in report
    for marker in documented_calibration_markers:
        assert marker in calibration_report
    assert "No reviewed recommendation outcomes found." in render_outcome_review([], {})
