from wraeclast_quant.config.connector_policy import connector_approval_patch
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_approval_patch_complete_conditional_review_changes_allowed_use_only() -> None:
    resources_markdown = """
## Price Data
- id: conditional_api
  name: Conditional API
  type: price_site
  url: https://example.test/api
  allowed_use: manual-or-api-if-available
  notes: keep this private
"""
    resource = Resource(
        id="conditional_api",
        name="Conditional API",
        type="price_site",
        url="https://example.test/api",
        allowed_use="manual-or-api-if-available",
        notes="keep this private",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "-  allowed_use: manual-or-api-if-available" in result.patch_text
    assert "+  allowed_use: api" in result.patch_text
    assert "notes" not in result.patch_text
    assert "https://example.test/api" not in result.patch_text


def test_connector_approval_patch_incomplete_evidence_has_no_patch() -> None:
    resource = Resource(
        name="Conditional API",
        type="price_site",
        url="https://example.test/api",
        allowed_use="manual-or-api-if-available",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API", source_terms_url=""),
        [resource],
        "- name: Conditional API\n  allowed_use: manual-or-api-if-available\n",
    )

    assert result.patch_available is False
    assert result.patch_text == ""
    assert "source_terms_url is required" in "\n".join(result.blockers)


def test_connector_approval_patch_discord_and_missing_resource_have_no_patch() -> None:
    missing = connector_approval_patch(
        _review(resource_name="Missing Source"),
        [],
        "",
    )
    discord = connector_approval_patch(
        _review(resource_name="Official Discord"),
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ],
        "- name: Official Discord\n  allowed_use: api\n",
    )

    assert missing.patch_available is False
    assert "No matching resource" in missing.reason
    assert discord.patch_available is False
    assert "Discord" in discord.reason


def test_connector_approval_patch_already_eligible_has_no_patch() -> None:
    result = connector_approval_patch(
        _review(),
        [_eligible_resource()],
        "- name: Approved API\n  allowed_use: api\n",
    )

    assert result.patch_available is False
    assert result.patch_text == ""
    assert "already automation-eligible" in result.reason
