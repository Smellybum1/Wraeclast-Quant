from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.connector_fixtures import ConnectorFixtureItem
from wraeclast_quant.config.fetch_policy import FetchPlan


class ConnectorResult(BaseModel):
    connector_id: str
    connector_class: str
    resource_name: str
    rows: list[ConnectorFixtureItem]
    fetch_plan: FetchPlan


__all__ = ["ConnectorResult"]
