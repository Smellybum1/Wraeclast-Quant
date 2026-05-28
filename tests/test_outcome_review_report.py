from pathlib import Path

from wraeclast_quant.reports.outcome_review import render_outcome_review, write_outcome_review

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
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md" in report
    assert "wq record-outcomes --input-path data/processed/outcome_decisions_run_<id>.json --dry-run" in report
    assert "positive=useful signal" in report
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
