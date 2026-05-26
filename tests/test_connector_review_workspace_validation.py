from pathlib import Path

import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    prepare_connector_review_workspace,
)

from connector_policy_helpers import discord_resource as _discord_resource
from connector_policy_helpers import eligible_resource as _eligible_resource


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
            resources=[_discord_resource()],
            output_dir=tmp_path,
        )
