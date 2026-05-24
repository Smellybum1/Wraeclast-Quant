from __future__ import annotations

from pathlib import Path

from wraeclast_quant.collectors.source_connector_base import SourceConnector
from wraeclast_quant.collectors.source_connector_models import ConnectorResult
from wraeclast_quant.config.connector_fixtures import run_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource


class FixtureSourceConnector(SourceConnector):
    connector_id = "fixture-source-connector"

    @classmethod
    def from_review(
        cls,
        review: ConnectorReview,
        resources: list[Resource],
    ) -> "FixtureSourceConnector":
        plan_result = build_fetch_plan(review, resources)
        if plan_result.plan is None or plan_result.check.resource is None:
            blockers = "\n".join(plan_result.check.blockers)
            raise ConnectorPolicyError(blockers or "Connector review is not ready.")
        return cls(
            resource=plan_result.check.resource,
            review=review,
            fetch_plan=plan_result.plan,
        )

    def collect_fixture(self, fixture_path: str | Path) -> ConnectorResult:
        result = run_connector_fixture(self.review, [self.resource], fixture_path)
        if not result.ready or result.fetch_plan is None:
            blockers = "\n".join(result.blockers)
            raise ConnectorPolicyError(blockers or "Connector fixture run failed.")

        return ConnectorResult(
            connector_id=self.connector_id,
            connector_class=self.__class__.__name__,
            resource_name=self.resource.name,
            rows=result.rows,
            fetch_plan=result.fetch_plan,
        )


__all__ = ["FixtureSourceConnector"]
