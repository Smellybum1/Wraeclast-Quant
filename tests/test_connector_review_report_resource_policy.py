from wraeclast_quant.config.connector_policy import connector_review_report

from connector_policy_helpers import conditional_api_resource as _conditional_api_resource
from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import discord_resource as _discord_resource


def test_connector_review_report_conditional_review_includes_approval_suggestion() -> None:
    report = connector_review_report(
        _review(resource_name="Conditional API"),
        [_conditional_api_resource()],
    )

    assert report.check_result.ready is False
    assert report.approval.suggestion_available is True
    assert "Approval suggestion: `allowed_use: api`" in report.markdown
    assert "manually update `RESOURCES.md` with `allowed_use: api`" in report.markdown


def test_connector_review_report_discord_or_missing_resource_has_no_suggestion() -> None:
    missing = connector_review_report(_review(resource_name="Missing Source"), [])
    discord = connector_review_report(
        _review(resource_name="Official Discord"),
        [_discord_resource()],
    )

    assert missing.approval.suggestion_available is False
    assert "Approval suggestion: `None`" in missing.markdown
    assert "No matching resource found in RESOURCES.md." in missing.markdown
    assert discord.approval.suggestion_available is False
    assert "Approval suggestion: `None`" in discord.markdown
    assert "Discord resources require explicit approved-bot/API review." in discord.markdown
