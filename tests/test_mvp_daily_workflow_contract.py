from pathlib import Path


def test_mvp_daily_workflow_uses_currency_exchange_review() -> None:
    text = Path("docs/MVP_DAILY_WORKFLOW.md").read_text(encoding="utf-8")

    assert "examples/reviews/pathofexile_currency_exchange_connector_review.json" in text
    assert "examples/connector_review_api_example.json" not in text
    assert "wq currency-exchange-manual-snapshot" in text
    assert "wq daily --input-path <manual-import-output>" in text
