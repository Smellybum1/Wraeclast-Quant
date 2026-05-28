from pathlib import Path


def test_mvp_daily_workflow_uses_currency_exchange_review() -> None:
    text = Path("docs/MVP_DAILY_WORKFLOW.md").read_text(encoding="utf-8")

    assert "examples/reviews/pathofexile_currency_exchange_connector_review.json" in text
    assert "examples/connector_review_api_example.json" not in text
    assert "wq currency-exchange-manual-snapshot" in text
    assert "wq daily --input-path <manual-import-output>" in text
    assert "Open the ratio/stock ladder and transcribe the visible rows" in text
    assert 'comparator: "less_than"' in text
    assert "ratio-only observations" in text
    assert "wq watchlist" in text
    assert "wq review-queue --run-id <id> --output-path data/processed/review_queue.md" in text
    assert "wq outcome-review" in text
    assert "wq calibration" in text
    assert "wq outcome-report --output-path data/processed/outcome_review.md" in text
    assert "wq calibration-report --output-path data/processed/calibration_report.md" in text
    assert "They do not retune scoring" in text
    assert "wq stash-ninja-watchlist" in text
    assert "do not write Exile-UI settings or caches" in text


def test_readme_generated_artifacts_include_local_mvp_handoffs() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "data/processed/review_queue.md" in text
    assert "data/processed/outcome_review.md" in text
    assert "data/processed/calibration_report.md" in text
    assert "data/processed/publish_handoff.md" in text
    assert "data/processed/exile_ui_stash_ninja_watchlist.json" in text
