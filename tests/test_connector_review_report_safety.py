from pathlib import Path

from wraeclast_quant.config.connector_policy import write_connector_review_report

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_review_report_excludes_notes_query_strings_and_raw_data(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "review_report.md"
    review = _review(
        source_terms_url="https://example.test/terms?token=SECRET",
        robots_or_api_policy_url="https://example.test/api-policy?cookie=SECRET",
        review_notes="token SECRET cookie .env demand_momentum raw fixture row",
    )

    write_connector_review_report(review, [_eligible_resource()], output_path)
    markdown = output_path.read_text(encoding="utf-8")

    assert "https://example.test/terms" in markdown
    assert "https://example.test/api-policy" in markdown
    assert "SECRET" not in markdown
    assert "token" not in markdown.casefold()
    assert "cookie" not in markdown.casefold()
    assert ".env" not in markdown
    assert "demand_momentum" not in markdown
    assert "raw fixture row" not in markdown
