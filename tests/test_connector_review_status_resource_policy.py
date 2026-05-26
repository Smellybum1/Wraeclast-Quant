from wraeclast_quant.config.connector_policy import connector_review_status

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import discord_resource as _discord_resource


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
        [_discord_resource(name="Approved API")],
    )
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Preflight"].value == "discord-gated"
    assert any("Discord" in blocker for blocker in status.check_result.blockers)
