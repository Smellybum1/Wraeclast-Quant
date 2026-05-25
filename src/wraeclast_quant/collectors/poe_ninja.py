from __future__ import annotations

from wraeclast_quant.collectors.source_connector_fixture import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


class PoeNinjaCurrencyConnector(FixtureSourceConnector):
    connector_id = "poe-ninja-poe2-currency"
    resource_id = "poe_ninja_poe2_currency"
    _LIVE_BLOCKERS = [
        "Live connector collection is unsupported for poe.ninja POE2 Currency.",
        "Missing confirmed official poe.ninja POE2 machine endpoint URL and query parameter contract.",
        "Missing official poe.ninja response-field schema for currency rows.",
        "Missing source-owner reuse, rate-limit, and cache policy confirmation for live HTTP.",
        "Use fixture dry-runs until the source review and live fetch design are updated.",
    ]

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

    def live_blockers(self) -> list[str]:
        return list(self._LIVE_BLOCKERS)
