from __future__ import annotations

from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_fixture import (
    load_currency_exchange_connector_fixture,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_live_policy import (
    official_currency_exchange_live_blockers,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime import (
    CurrencyExchangeRuntimePlan,
    CurrencyExchangeRuntimeSettings,
    preview_currency_exchange_runtime_plan,
)
from wraeclast_quant.collectors.source_connector_fixture import FixtureSourceConnector
from wraeclast_quant.collectors.source_connector_models import ConnectorResult
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


class OfficialCurrencyExchangeConnector(FixtureSourceConnector):
    connector_id = "official-currency-exchange-api"
    resource_id = "official_currency_exchange_api"

    @classmethod
    def from_review(
        cls,
        review: ConnectorReview,
        resources: list[Resource],
    ) -> "OfficialCurrencyExchangeConnector":
        connector = super().from_review(review, resources)
        if connector.resource.id != cls.resource_id:
            raise ConnectorPolicyError(
                "official Currency Exchange connector requires the official_currency_exchange_api resource."
            )
        return cls(
            resource=connector.resource,
            review=connector.review,
            fetch_plan=connector.fetch_plan,
        )

    def collect_fixture(self, fixture_path: str | Path) -> ConnectorResult:
        fixture = load_currency_exchange_connector_fixture(fixture_path)
        return ConnectorResult(
            connector_id=self.connector_id,
            connector_class=self.__class__.__name__,
            resource_name=self.resource.name,
            rows=fixture.items,
            fetch_plan=self.fetch_plan,
        )

    def live_blockers(self) -> list[str]:
        return official_currency_exchange_live_blockers()

    def preview_runtime_plan(
        self,
        settings: CurrencyExchangeRuntimeSettings,
        *,
        workspace_root: str | Path = Path.cwd(),
    ) -> CurrencyExchangeRuntimePlan:
        return preview_currency_exchange_runtime_plan(
            settings,
            self.fetch_plan,
            workspace_root=workspace_root,
        )


__all__ = ["OfficialCurrencyExchangeConnector"]
