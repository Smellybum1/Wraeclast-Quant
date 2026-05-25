import pytest

from wraeclast_quant.config.connector_candidates import connector_candidates, suggested_access_method
from wraeclast_quant.config.resources_loader import Resource


def test_connector_candidates_rank_needs_review_before_manual_review() -> None:
    candidates = connector_candidates(
        [
            Resource(name="Manual Source", allowed_use="manual-review", priority="critical"),
            Resource(
                name="Conditional API",
                id="conditional_api",
                allowed_use="api-or-manual-review",
                priority="medium",
                url="https://example.test/api",
            ),
        ]
    )

    assert [candidate.resource.name for candidate in candidates[:2]] == [
        "Conditional API",
        "Manual Source",
    ]
    assert candidates[0].preflight.status == "needs-review"
    assert "wq connector-draft" in candidates[0].draft_command


@pytest.mark.parametrize(
    ("allowed_use", "expected"),
    [
        ("api-or-manual-review", "api"),
        ("manual-or-api-if-available", "api"),
        ("manual-review-or-api-if-available", "api"),
        ("rss-or-manual-review", "rss"),
        ("download", "download"),
        ("manual-review", "manual-export"),
    ],
)
def test_connector_candidate_suggested_access_method_from_allowed_use(
    allowed_use: str,
    expected: str,
) -> None:
    assert suggested_access_method(Resource(name="Source", allowed_use=allowed_use)) == expected


def test_connector_candidates_mark_discord_as_compliance_gated() -> None:
    candidates = connector_candidates(
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ]
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
