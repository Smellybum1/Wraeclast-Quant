from pathlib import Path

import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
    check_connector_review,
    load_connector_review,
    prepare_connector_review_workspace,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import eligible_resource as _eligible_resource


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


def test_connector_review_draft_rejects_unsupported_access_method() -> None:
    with pytest.raises(ConnectorPolicyError, match="access_method"):
        build_connector_review_draft(
            resource_name="Approved API",
            access_method="browser",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_missing_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="No matching resource"):
        build_connector_review_draft(
            resource_name="Missing API",
            access_method="api",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_discord_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="Discord resources require explicit"):
        build_connector_review_draft(
            resource_name="Official Discord",
            access_method="api",
            resources=[
                Resource(
                    name="Official Discord",
                    type="discord",
                    url="https://discord.gg/example",
                    allowed_use="api",
                )
            ],
        )


def test_connector_review_draft_defaults_are_conservative_and_not_ready() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="api",
        resources=[_eligible_resource()],
    )
    result = check_connector_review(review, [_eligible_resource()])

    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert review.authentication_required is False
    assert review.login_required is False
    assert review.captcha_gated is False
    assert review.private_data_risk is False
    assert review.rate_limit_per_minute == 6
    assert review.cache_ttl_seconds == 86400
    assert review.dry_run_supported is True
    assert review.public_export_derived_only is True
    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers
    assert "Robots.txt or API policy must be reviewed." in result.blockers


def test_connector_review_prep_resolves_resource_and_writes_workspace(
    tmp_path: Path,
) -> None:
    prep = prepare_connector_review_workspace(
        resource_name="poe_ninja_poe2_currency",
        access_method="api",
        resources=[
            Resource(
                id="poe_ninja_poe2_currency",
                name="poe.ninja POE2 Currency",
                type="price_site",
                url="https://poe.ninja/poe2/economy/vaal/currency",
                allowed_use="manual-or-api-if-available",
            )
        ],
        output_dir=tmp_path,
    )
    review = load_connector_review(prep.review_path)
    checklist = prep.checklist_path.read_text(encoding="utf-8")
    result = check_connector_review(review, [_eligible_resource()])

    assert prep.review_path == tmp_path / "poe_ninja_poe2_currency_connector_review.json"
    assert prep.checklist_path == tmp_path / "poe_ninja_poe2_currency_review_checklist.md"
    assert review.resource_name == "poe.ninja POE2 Currency"
    assert review.access_method == "api"
    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert "Source terms URL" in checklist
    assert "Robots.txt or API policy URL" in checklist
    assert "Allowed data shape" in checklist
    assert "Dry-run support confirmed" in checklist
    assert any("connector-review-status" in command for command in prep.next_commands)
    assert result.ready is False


def test_connector_review_prep_rejects_missing_resource(tmp_path: Path) -> None:
    with pytest.raises(ConnectorPolicyError, match="No matching resource"):
        prepare_connector_review_workspace(
            resource_name="missing",
            access_method="api",
            resources=[_eligible_resource()],
            output_dir=tmp_path,
        )


def test_connector_review_prep_rejects_discord_resource(tmp_path: Path) -> None:
    with pytest.raises(ConnectorPolicyError, match="Discord resources require explicit"):
        prepare_connector_review_workspace(
            resource_name="Official Discord",
            access_method="api",
            resources=[
                Resource(
                    name="Official Discord",
                    type="discord",
                    url="https://discord.gg/example",
                    allowed_use="api",
                )
            ],
            output_dir=tmp_path,
        )


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
