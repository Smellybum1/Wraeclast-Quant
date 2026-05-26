from wraeclast_quant.config.connector_policy import build_connector_review_draft

from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import eligible_rss_resource as _eligible_rss_resource


def test_connector_review_draft_resolves_resource_by_id() -> None:
    review = build_connector_review_draft(
        resource_name="approved_api",
        access_method="api",
        resources=[_eligible_resource(resource_id="approved_api")],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "api"


def test_connector_review_draft_resolves_resource_by_name() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="rss",
        resources=[_eligible_rss_resource(resource_id="approved_api")],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "rss"
