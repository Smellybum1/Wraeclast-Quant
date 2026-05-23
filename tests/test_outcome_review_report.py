from pathlib import Path

from wraeclast_quant.reports.calibration import (
    SCORE_BUCKETS,
    build_calibration,
    render_calibration_report,
    score_bucket,
    write_calibration_report,
)
from wraeclast_quant.reports.outcome_review import render_outcome_review, write_outcome_review
from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository


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


def test_calibration_empty_missing_database_is_non_mutating(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = build_calibration(SnapshotRepository(database_path))

    assert result.has_outcomes is False
    assert result.reviews == []
    assert result.recent_reviews == []
    assert result.by_action == {}
    assert set(result.by_score_bucket) == set(SCORE_BUCKETS)
    assert result.average_score_by_outcome == {
        "negative": None,
        "neutral": None,
        "positive": None,
    }
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_calibration_groups_by_action_score_bucket_and_average() -> None:
    result = render_calibration_report(
        result := build_calibration_from_reviews(
            [
                _review(item_name="Buy Good", action="BUY", outcome="positive", score=76.0),
                _review(item_name="Watch Bad", action="WATCH", outcome="negative", score=60.0),
                _review(item_name="Hold Neutral", action="HOLD / SELL SELECTIVELY", outcome="neutral", score=40.0),
                _review(item_name="Avoid Good", action="AVOID", outcome="positive", score=20.0),
            ]
        )
    )

    assert result
    assert "| BUY | 0 | 0 | 1 |" in result
    assert "| WATCH | 1 | 0 | 0 |" in result
    assert "| 75+ | 0 | 0 | 1 |" in result
    assert "| 55-74.99 | 1 | 0 | 0 |" in result
    assert "| 35-54.99 | 0 | 1 | 0 |" in result
    assert "| <35 | 0 | 0 | 1 |" in result
    assert "| positive | 48.00 |" in result
    assert "| negative | 60.00 |" in result
    assert "| neutral | 40.00 |" in result


def test_calibration_recent_reviews_respect_limit() -> None:
    calibration = build_calibration_from_reviews(
        [
            _review(id=3, item_name="Newest"),
            _review(id=2, item_name="Middle"),
            _review(id=1, item_name="Oldest"),
        ],
        limit=2,
    )

    assert [review.item_name for review in calibration.recent_reviews] == ["Newest", "Middle"]


def test_calibration_score_bucket_boundaries() -> None:
    assert score_bucket(75.0) == "75+"
    assert score_bucket(55.0) == "55-74.99"
    assert score_bucket(35.0) == "35-54.99"
    assert score_bucket(34.99) == "<35"


def test_calibration_report_renders_empty_message() -> None:
    report = render_calibration_report(build_calibration_from_reviews([]))

    assert "No reviewed recommendation outcomes found." in report
    assert "Outcome Counts By Action" not in report


def test_write_calibration_report_creates_parent_directory(tmp_path: Path) -> None:
    output_path = write_calibration_report(
        build_calibration_from_reviews([_review()]),
        path=tmp_path / "reports" / "calibration_report.md",
    )

    assert output_path.exists()
    assert "Wraeclast Quant Recommendation Calibration" in output_path.read_text(encoding="utf-8")


def _review(
    id: int = 1,
    item_name: str = "Stormglass Catalyst",
    action: str = "BUY",
    outcome: str = "positive",
    notes: str = "",
    score: float = 76.0,
) -> OutcomeReviewRecord:
    return OutcomeReviewRecord(
        id=id,
        run_id=7,
        item_name=item_name,
        outcome=outcome,
        notes=notes,
        observed_at="2026-05-23T00:00:00+00:00",
        opportunity_score=score,
        action=action,
    )


def build_calibration_from_reviews(
    reviews: list[OutcomeReviewRecord],
    limit: int = 20,
):
    class FakeRepository:
        def list_outcome_reviews(self, limit=None):
            if limit is None:
                return reviews
            return reviews[:limit]

    return build_calibration(FakeRepository(), limit=limit)  # type: ignore[arg-type]


def _documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }
