from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from wraeclast_quant.config.connector_fixtures import (
    ConnectorFixtureItem,
    run_connector_fixture,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.fetch_policy import FetchPlan, build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource


class ConnectorResult(BaseModel):
    connector_id: str
    connector_class: str
    resource_name: str
    rows: list[ConnectorFixtureItem]
    fetch_plan: FetchPlan


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

    def collect_live(self) -> ConnectorResult:
        raise ConnectorPolicyError(
            "Live connector collection is unsupported in the MVP; use fixture dry-runs only."
        )


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


def source_connector_from_review(
    review: ConnectorReview,
    resources: list[Resource],
) -> SourceConnector:
    connector = FixtureSourceConnector.from_review(review, resources)
    if connector.resource.id == "poe_ninja_poe2_currency":
        from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector

        return PoeNinjaCurrencyConnector(
            resource=connector.resource,
            review=connector.review,
            fetch_plan=connector.fetch_plan,
        )
    return connector
