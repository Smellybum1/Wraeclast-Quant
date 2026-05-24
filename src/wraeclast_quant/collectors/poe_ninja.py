from __future__ import annotations

from wraeclast_quant.collectors.source_connector_fixture import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


class PoeNinjaCurrencyConnector(FixtureSourceConnector):
    connector_id = "poe-ninja-poe2-currency"
    resource_id = "poe_ninja_poe2_currency"

    @classmethod
    def from_review(
        cls,
        review: ConnectorReview,
        resources: list[Resource],
    ) -> "PoeNinjaCurrencyConnector":
        connector = super().from_review(review, resources)
        if connector.resource.id != cls.resource_id:
            raise ConnectorPolicyError(
                "poe.ninja currency connector requires the poe_ninja_poe2_currency resource."
            )
        return cls(
            resource=connector.resource,
            review=connector.review,
            fetch_plan=connector.fetch_plan,
        )
