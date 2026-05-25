from pathlib import Path

import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    check_connector_review,
    load_connector_review,
    prepare_connector_review_workspace,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import eligible_resource as _eligible_resource


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
