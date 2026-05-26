from wraeclast_quant.config.connector_policy import (
    build_connector_review_draft,
    update_connector_review_evidence,
)

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_review_evidence_source_terms_url_sets_reviewed() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        source_terms_url="https://example.test/terms",
    )

    assert updated.source_terms_reviewed is True
    assert updated.source_terms_url == "https://example.test/terms"
    assert updated.robots_or_api_policy_reviewed is False


def test_connector_review_evidence_policy_url_sets_reviewed() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        robots_or_api_policy_url="https://example.test/api-policy",
    )

    assert updated.robots_or_api_policy_reviewed is True
    assert updated.robots_or_api_policy_url == "https://example.test/api-policy"
    assert updated.source_terms_reviewed is False


def test_connector_review_evidence_preserves_omitted_fields() -> None:
    review = _review(review_notes="Existing note.", rate_limit_per_minute=12)

    updated = update_connector_review_evidence(
        review,
        reviewed_at="2026-05-23",
        allowed_data_shape="Derived currency summary rows only.",
    )

    assert updated.review_notes == "Existing note."
    assert updated.rate_limit_per_minute == 12
    assert updated.reviewed_at == "2026-05-23"
    assert updated.allowed_data_shape == "Derived currency summary rows only."


def test_connector_review_evidence_updates_auth_approval_fields() -> None:
    review = build_connector_review_draft("Approved API", "api", [_eligible_resource()])

    updated = update_connector_review_evidence(
        review,
        authentication_required=True,
        authentication_approved=True,
        credential_storage_reviewed=True,
    )

    assert updated.authentication_required is True
    assert updated.authentication_approved is True
    assert updated.credential_storage_reviewed is True
