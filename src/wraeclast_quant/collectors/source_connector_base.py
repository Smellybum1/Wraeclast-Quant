from __future__ import annotations

from pathlib import Path

from wraeclast_quant.collectors.source_connector_models import ConnectorResult
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.fetch_policy import FetchPlan
from wraeclast_quant.config.resources_loader import Resource


class SourceConnector:
    connector_id = "source-connector"

    def __init__(
        self,
        resource: Resource,
        review: ConnectorReview,
        fetch_plan: FetchPlan,
    ) -> None:
        self.resource = resource
        self.review = review
        self.fetch_plan = fetch_plan

    def collect_fixture(self, fixture_path: str | Path) -> ConnectorResult:
        raise NotImplementedError

    def live_blockers(self) -> list[str]:
        return ["Live connector collection is unsupported in the MVP; use fixture dry-runs only."]

    def collect_live(self) -> ConnectorResult:
        raise ConnectorPolicyError("\n".join(self.live_blockers()))


__all__ = ["SourceConnector"]
