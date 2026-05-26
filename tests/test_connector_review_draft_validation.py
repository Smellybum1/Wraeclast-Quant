import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_review_draft_rejects_unsupported_access_method() -> None:
    with pytest.raises(ConnectorPolicyError, match="access_method"):
        build_connector_review_draft(
            resource_name="Approved API",
            access_method="browser",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_missing_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="No matching resource"):
        build_connector_review_draft(
            resource_name="Missing API",
            access_method="api",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_discord_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="Discord resources require explicit"):
        build_connector_review_draft(
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
        )
