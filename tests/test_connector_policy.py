from wraeclast_quant.config.connector_policy import (
    check_connector_review,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


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
