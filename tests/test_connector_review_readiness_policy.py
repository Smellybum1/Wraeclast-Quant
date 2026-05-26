from wraeclast_quant.config.connector_policy import check_connector_review
from wraeclast_quant.config.resources_loader import Resource

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
