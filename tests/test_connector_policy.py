from pathlib import Path

import pytest

from wraeclast_quant.config.connector_policy import (
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


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


def test_missing_resource_fails_clearly() -> None:
    result = check_connector_review(_review(), [])

    assert result.ready is False
    assert "No matching resource found in RESOURCES.md." in result.blockers


def test_preflight_ineligible_resource_fails() -> None:
    result = check_connector_review(
        _review(),
        [Resource(name="Approved API", allowed_use="manual-review")],
    )

    assert result.ready is False
    assert any("not automation-eligible" in blocker for blocker in result.blockers)


def test_discord_review_fails_even_if_fields_look_permissive() -> None:
    result = check_connector_review(
        _review(),
        [
            Resource(
                name="Approved API",
                type="discord",
                url="https://discord.com/channels/example",
                allowed_use="api",
            )
        ],
    )

    assert result.ready is False
    assert any("Discord" in blocker for blocker in result.blockers)


def test_missing_terms_or_policy_review_fails() -> None:
    result = check_connector_review(
        _review(source_terms_reviewed=False, robots_or_api_policy_reviewed=False),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers
    assert "Robots.txt or API policy must be reviewed." in result.blockers


def test_missing_source_terms_url_blocks_when_terms_are_marked_reviewed() -> None:
    result = check_connector_review(
        _review(source_terms_url=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "source_terms_url is required when source terms are reviewed." in result.blockers


def test_missing_robots_or_api_policy_url_blocks_when_policy_is_marked_reviewed() -> None:
    result = check_connector_review(
        _review(robots_or_api_policy_url=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert (
        "robots_or_api_policy_url is required when robots/API policy is reviewed."
        in result.blockers
    )


def test_missing_reviewed_at_blocks_when_review_confirmations_are_complete() -> None:
    result = check_connector_review(
        _review(reviewed_at=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "reviewed_at is required when review confirmations are complete." in result.blockers


def test_missing_allowed_data_shape_blocks_when_review_confirmations_are_complete() -> None:
    result = check_connector_review(
        _review(allowed_data_shape=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert (
        "allowed_data_shape is required when review confirmations are complete."
        in result.blockers
    )


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("authentication_required", "Authentication-required"),
        ("login_required", "Login-required"),
        ("captcha_gated", "CAPTCHA-gated"),
        ("private_data_risk", "Private data"),
    ],
)
def test_auth_login_captcha_or_private_data_flags_fail(field: str, expected: str) -> None:
    result = check_connector_review(_review(**{field: True}), [_eligible_resource()])

    assert result.ready is False
    assert any(expected in blocker for blocker in result.blockers)


def test_non_positive_cache_or_rate_limit_fails() -> None:
    result = check_connector_review(
        _review(rate_limit_per_minute=0, cache_ttl_seconds=0),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "rate_limit_per_minute must be positive." in result.blockers
    assert "cache_ttl_seconds must be positive." in result.blockers


def test_missing_dry_run_or_derived_only_export_confirmation_fails() -> None:
    result = check_connector_review(
        _review(dry_run_supported=False, public_export_derived_only=False),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "Dry-run support must be explicitly confirmed." in result.blockers
    assert "Public export must be derived-only." in result.blockers


def test_unsupported_access_method_fails() -> None:
    result = check_connector_review(_review(access_method="browser"), [_eligible_resource()])

    assert result.ready is False
    assert any("access_method" in blocker for blocker in result.blockers)
