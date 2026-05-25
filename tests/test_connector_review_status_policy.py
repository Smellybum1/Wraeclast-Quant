import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
    check_connector_review,
    connector_review_status,
    load_connector_review,
    update_connector_review_evidence,
)
from wraeclast_quant.config.resources_loader import Resource

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


def test_connector_review_status_reports_incomplete_draft_blockers() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="api",
        resources=[_eligible_resource()],
    )
    status = connector_review_status(review, [_eligible_resource()])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Resource match"].status == "ok"
    assert row_by_check["Source terms reviewed"].value == "no"
    assert row_by_check["Source terms reviewed"].status == "needs-review"
    assert row_by_check["Source terms URL"].status == "needs-review"
    assert row_by_check["Robots/API policy reviewed"].status == "needs-review"
    assert row_by_check["Robots/API policy URL"].status == "needs-review"
    assert row_by_check["Reviewed at"].status == "optional"
    assert row_by_check["Allowed data shape"].status == "optional"
    assert row_by_check["Readiness"].value == "not ready"
    assert "Source terms must be reviewed." in status.check_result.blockers


def test_connector_review_status_reports_ready_review() -> None:
    status = connector_review_status(_review(), [_eligible_resource()])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is True
    assert row_by_check["Preflight"].status == "ok"
    assert row_by_check["Source terms URL"].status == "ok"
    assert row_by_check["Robots/API policy URL"].status == "ok"
    assert row_by_check["Reviewed at"].status == "ok"
    assert row_by_check["Allowed data shape"].status == "ok"
    assert row_by_check["Readiness"].value == "ready"
    assert status.check_result.blockers == []


def test_connector_review_status_marks_missing_claimed_evidence_blocked() -> None:
    status = connector_review_status(
        _review(
            source_terms_url="",
            robots_or_api_policy_url="",
            reviewed_at="",
            allowed_data_shape="",
        ),
        [_eligible_resource()],
    )
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Source terms reviewed"].status == "ok"
    assert row_by_check["Source terms URL"].status == "blocked"
    assert row_by_check["Robots/API policy URL"].status == "blocked"
    assert row_by_check["Reviewed at"].status == "blocked"
    assert row_by_check["Allowed data shape"].status == "blocked"


def test_connector_review_status_reports_missing_resource_as_blocked() -> None:
    status = connector_review_status(_review(), [])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Resource match"].status == "blocked"
    assert row_by_check["Preflight"].value == "missing"
    assert "No matching resource found in RESOURCES.md." in status.check_result.blockers


def test_connector_review_status_keeps_discord_blocked() -> None:
    status = connector_review_status(
        _review(),
        [
            Resource(
                name="Approved API",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ],
    )
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Preflight"].value == "discord-gated"
    assert any("Discord" in blocker for blocker in status.check_result.blockers)


def test_poe_ninja_currency_review_workspace_is_incomplete() -> None:
    review = load_connector_review("examples/poe_ninja_poe2_currency_connector_review.json")
    result = check_connector_review(
        review,
        [
            Resource(
                id="poe_ninja_poe2_currency",
                name="poe.ninja POE2 Currency",
                type="price_site",
                url="https://poe.ninja/poe2/economy/vaal/currency",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers
