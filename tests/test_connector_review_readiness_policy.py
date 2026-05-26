from pathlib import Path

from wraeclast_quant.config.connector_policy import (
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource, load_resources

from connector_policy_helpers import connector_review as _review


def test_valid_api_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(),
        [
            Resource(
                name="Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
    )

    assert result.ready is True
    assert result.blockers == []


def test_valid_rss_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="rss"),
        [
            Resource(
                name="Approved API",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            )
        ],
    )

    assert result.ready is True


def test_valid_download_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="download", resource_name="Approved Download"),
        [
            Resource(
                name="Approved Download",
                type="official",
                url="https://example.test/data.json",
                allowed_use="download",
            )
        ],
    )

    assert result.ready is True
    assert result.blockers == []


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


def test_official_currency_exchange_review_requires_resource_match() -> None:
    review = load_connector_review(
        Path("examples/reviews/pathofexile_currency_exchange_connector_review.json")
    )
    result = check_connector_review(review, [])
    plan = build_fetch_plan(review, [])

    assert result.ready is False
    assert "No matching resource found in RESOURCES.md." in result.blockers
    assert plan.plan is None


def test_official_currency_exchange_review_passes_after_source_and_auth_approval() -> None:
    review = load_connector_review(
        Path("examples/reviews/pathofexile_currency_exchange_connector_review.json")
    )
    resources = load_resources(Path("RESOURCES.md"))
    result = check_connector_review(review, resources)
    plan = build_fetch_plan(review, resources)

    assert result.ready is True
    assert result.blockers == []
    assert result.preflight is not None
    assert result.preflight.status == "approved-api"
    assert plan.plan is not None
    assert plan.plan.cache_ttl_seconds == 3600
