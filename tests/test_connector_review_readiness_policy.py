from wraeclast_quant.config.connector_policy import check_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_download_resource as _eligible_download_resource
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import eligible_rss_resource as _eligible_rss_resource


def test_valid_api_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(),
        [_eligible_resource()],
    )

    assert result.ready is True
    assert result.blockers == []


def test_valid_rss_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="rss"),
        [_eligible_rss_resource()],
    )

    assert result.ready is True


def test_valid_download_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="download", resource_name="Approved Download"),
        [_eligible_download_resource()],
    )

    assert result.ready is True
    assert result.blockers == []
