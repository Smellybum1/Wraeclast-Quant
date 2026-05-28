from pathlib import Path

from wraeclast_quant.reports.calibration import (
    SCORE_BUCKETS,
    build_calibration,
    render_calibration_report,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

from outcome_review_helpers import build_calibration_from_reviews
from outcome_review_helpers import review_record as _review


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
    assert "## Calibration Review Prompts" in result
    assert "AVOID has 1 positive outcome(s)" in result
    assert "WATCH has 1 negative outcome(s)" in result


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


def test_calibration_report_renders_empty_message() -> None:
    report = render_calibration_report(build_calibration_from_reviews([]))

    assert "No reviewed recommendation outcomes found." in report
    assert "wq review-queue" in report
    assert "positive=useful signal" in report
    assert "Outcome Counts By Action" not in report
