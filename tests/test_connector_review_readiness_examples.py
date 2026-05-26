from pathlib import Path

from wraeclast_quant.config.connector_policy import (
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource


def test_example_connector_review_files_are_ready_for_matching_resources() -> None:
    cases = [
        (
            Path("examples/connector_review_api_example.json"),
            Resource(
                name="Example Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            ),
            "api",
        ),
        (
            Path("examples/connector_review_rss_example.json"),
            Resource(
                name="Example Approved RSS",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            ),
            "rss",
        ),
        (
            Path("examples/connector_review_download_example.json"),
            Resource(
                name="Example Approved Download",
                type="official",
                url="https://example.test/data.json",
                allowed_use="download",
            ),
            "download",
        ),
    ]

    for review_path, resource, access_method in cases:
        review = load_connector_review(review_path)
        check = check_connector_review(review, [resource])
        plan = build_fetch_plan(review, [resource])

        assert review.access_method == access_method
        assert check.ready is True
        assert check.blockers == []
        assert plan.plan is not None
        assert plan.plan.access_method == access_method
