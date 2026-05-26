import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
    check_connector_review,
    update_connector_review_evidence,
)

from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_review_evidence_rejects_invalid_rate_limit_or_cache_ttl() -> None:
    review = build_connector_review_draft("Approved API", "api", [_eligible_resource()])

    with pytest.raises(ConnectorPolicyError, match="rate_limit_per_minute"):
        update_connector_review_evidence(review, rate_limit_per_minute=0)

    with pytest.raises(ConnectorPolicyError, match="cache_ttl_seconds"):
        update_connector_review_evidence(review, cache_ttl_seconds=0)


def test_connector_review_evidence_complete_review_can_pass_evidence_gate() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        source_terms_url="https://example.test/terms",
        robots_or_api_policy_url="https://example.test/api-policy",
        reviewed_at="2026-05-23",
        allowed_data_shape="Derived currency summary rows only.",
        review_notes="Manual review completed.",
        rate_limit_per_minute=30,
        cache_ttl_seconds=3600,
    )
    result = check_connector_review(updated, [_eligible_resource()])

    assert result.ready is True
    assert result.blockers == []
