from wraeclast_quant.config.preflight import assess_preflight_resource
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import discord_resource as _discord_resource


def test_preflight_api_missing_url_is_ineligible() -> None:
    assessment = assess_preflight_resource(
        Resource(name="Missing URL API", type="official", allowed_use="api")
    )

    assert assessment.status == "needs-review"
    assert assessment.automation_eligible is False
    assert "missing a URL" in assessment.reason


def test_preflight_discord_is_gated_even_if_marked_api() -> None:
    assessment = assess_preflight_resource(
        _discord_resource(url="https://discord.com/channels/example")
    )

    assert assessment.status == "discord-gated"
    assert assessment.automation_eligible is False
    assert "approved-bot/API" in assessment.reason


def test_preflight_manual_and_blocked_sources_are_ineligible() -> None:
    manual = assess_preflight_resource(
        Resource(name="Manual Source", allowed_use="manual-review")
    )
    blocked = assess_preflight_resource(
        Resource(name="Blocked Source", allowed_use="no-automation")
    )

    assert manual.status == "manual-review"
    assert manual.automation_eligible is False
    assert blocked.status == "blocked"
    assert blocked.automation_eligible is False
