from wraeclast_quant.config.connector_policy import connector_approval_patch

from connector_policy_helpers import conditional_api_resource as _conditional_api_resource
from connector_policy_helpers import connector_review as _review


def test_connector_approval_patch_sanitizes_patch_preview() -> None:
    resources_markdown = """
## Price Data
- id: conditional_api
  name: Conditional API
  type: price_site
  url: https://example.test/api?token=SECRET
  allowed_use: manual-or-api-if-available
  notes: cookie SECRET .env demand_momentum raw fixture row
"""
    resource = _conditional_api_resource(
        url="https://example.test/api?token=SECRET",
        notes="cookie SECRET .env demand_momentum raw fixture row",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "allowed_use: api" in result.patch_text
    assert "SECRET" not in result.patch_text
    assert "cookie" not in result.patch_text.casefold()
    assert ".env" not in result.patch_text
    assert "demand_momentum" not in result.patch_text
    assert "raw fixture row" not in result.patch_text


def test_connector_approval_patch_preserves_escaped_allowed_use_key() -> None:
    resources_markdown = """
## Price Data
\\- id: conditional\\_api
&#x20; name: Conditional API
&#x20; type: price\\_site
&#x20; url: https://example.test/api
&#x20; allowed\\_use: manual-or-api-if-available
"""
    resource = _conditional_api_resource()

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "-&#x20; allowed\\_use: manual-or-api-if-available" in result.patch_text
    assert "+&#x20; allowed\\_use: api" in result.patch_text
