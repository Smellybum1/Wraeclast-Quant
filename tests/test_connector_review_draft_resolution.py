from wraeclast_quant.config.connector_policy import build_connector_review_draft
from wraeclast_quant.config.resources_loader import Resource


def test_connector_review_draft_resolves_resource_by_id() -> None:
    review = build_connector_review_draft(
        resource_name="approved_api",
        access_method="api",
        resources=[
            Resource(
                id="approved_api",
                name="Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "api"


def test_connector_review_draft_resolves_resource_by_name() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="rss",
        resources=[
            Resource(
                id="approved_api",
                name="Approved API",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            )
        ],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "rss"
