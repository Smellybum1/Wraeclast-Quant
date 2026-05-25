from wraeclast_quant.config.connector_policy import (
    connector_approval_helper,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_approval_helper_suggests_allowed_use_for_complete_conditional_review() -> None:
    result = connector_approval_helper(
        _review(resource_name="Conditional API"),
        [
            Resource(
                id="conditional_api",
                name="Conditional API",
                type="price_site",
                url="https://example.test/api",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert result.suggestion_available is True
    assert result.approval_suggestion == "allowed_use: api"
    assert result.evidence_ready is True
    assert result.connector_check_ready is False


def test_connector_approval_helper_with_incomplete_evidence_has_no_suggestion() -> None:
    result = connector_approval_helper(
        _review(resource_name="Conditional API", source_terms_url=""),
        [
            Resource(
                name="Conditional API",
                url="https://example.test/api",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert result.suggestion_available is False
    assert result.approval_suggestion == "None"
    assert result.evidence_ready is False
    assert "source_terms_url is required" in "\n".join(result.blockers)


def test_connector_approval_helper_has_no_suggestion_for_discord() -> None:
    result = connector_approval_helper(
        _review(resource_name="Official Discord"),
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert result.suggestion_available is False
    assert "Discord" in result.reason


def test_connector_approval_helper_has_no_suggestion_for_missing_resource() -> None:
    result = connector_approval_helper(_review(resource_name="Missing Source"), [])

    assert result.suggestion_available is False
    assert result.resource is None
    assert "No matching resource" in result.reason


def test_connector_approval_helper_reports_no_change_for_already_eligible_resource() -> None:
    result = connector_approval_helper(_review(), [_eligible_resource()])

    assert result.suggestion_available is False
    assert result.connector_check_ready is True
    assert result.approval_suggestion == "None"
    assert "already automation-eligible" in result.reason


