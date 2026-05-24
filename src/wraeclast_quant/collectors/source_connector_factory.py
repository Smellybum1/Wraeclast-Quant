from __future__ import annotations

from wraeclast_quant.collectors.source_connector_base import SourceConnector
from wraeclast_quant.collectors.source_connector_fixture import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


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


__all__ = ["source_connector_from_review"]
