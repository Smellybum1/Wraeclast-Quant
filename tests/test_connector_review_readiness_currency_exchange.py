from pathlib import Path

from wraeclast_quant.config.connector_policy import (
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import load_resources


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
