from wraeclast_quant.config.connector_candidates import connector_candidates
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import conditional_api_resource as _conditional_api_resource
from connector_policy_helpers import discord_resource as _discord_resource


def test_connector_candidates_rank_needs_review_before_manual_review() -> None:
    candidates = connector_candidates(
        [
            Resource(name="Manual Source", allowed_use="manual-review", priority="critical"),
            _conditional_api_resource(
                resource_type=None,
                allowed_use="api-or-manual-review",
                priority="medium",
            ),
        ]
    )

    assert [candidate.resource.name for candidate in candidates[:2]] == [
        "Conditional API",
        "Manual Source",
    ]
    assert candidates[0].preflight.status == "needs-review"
    assert "wq connector-draft" in candidates[0].draft_command

def test_connector_candidates_mark_discord_as_compliance_gated() -> None:
    candidates = connector_candidates(
        [_discord_resource()]
    )

    assert candidates[0].preflight.status == "discord-gated"
    assert candidates[0].draft_command == ""
    assert "Discord-gated" in candidates[0].recommendation


def test_connector_candidates_respect_limit() -> None:
    candidates = connector_candidates(
        [
            Resource(name="First", allowed_use="api-or-manual-review", url="https://example.test/1"),
            Resource(name="Second", allowed_use="api-or-manual-review", url="https://example.test/2"),
        ],
        limit=1,
    )

    assert len(candidates) == 1


def test_connector_candidates_missing_id_uses_name_in_draft_command() -> None:
    candidates = connector_candidates(
        [
            Resource(
                name="Conditional API Source",
                allowed_use="api-or-manual-review",
                url="https://example.test/api",
            )
        ]
    )

    assert '--resource "Conditional API Source"' in candidates[0].draft_command
    assert "conditional_api_source_connector_review.json" in candidates[0].draft_command
