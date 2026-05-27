from pathlib import Path


def test_mvp_daily_workflow_uses_currency_exchange_review() -> None:
    text = Path("docs/MVP_DAILY_WORKFLOW.md").read_text(encoding="utf-8")

    assert "examples/reviews/pathofexile_currency_exchange_connector_review.json" in text
    assert "examples/connector_review_api_example.json" not in text
    assert "wq currency-exchange-manual-snapshot" in text
    assert "wq daily --input-path <manual-import-output>" in text
    assert "wq watchlist" in text
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue.md" in text
    assert "wq outcome-review" in text
    assert "wq calibration" in text
    assert "wq outcome-report --output-path data/processed/outcome_review.md" in text
    assert "wq calibration-report --output-path data/processed/calibration_report.md" in text
    assert "They do not retune scoring" in text
    assert "wq stash-ninja-watchlist" in text
    assert "do not write Exile-UI settings or caches" in text
