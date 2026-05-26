from __future__ import annotations

from datetime import UTC, datetime

from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_preview import (
    preview_currency_exchange_rolling_baseline_diagnostics,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_fixture import (
    currency_exchange_market_item,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import clamp_score
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixture,
    ConnectorFixtureItem,
)
from wraeclast_quant.intelligence.scoring import OpportunityInputs


def preview_currency_exchange_signal_fixture_from_baseline(
    payload: CurrencyExchangePayload,
    history: list[CurrencyExchangePayload],
    *,
    min_observations: int = 1,
) -> ConnectorFixture:
    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        payload,
        history,
        min_observations=min_observations,
    )
    generated_at = datetime.fromtimestamp(payload.next_change_id, tz=UTC).isoformat()
    return ConnectorFixture(
        source_name="Path of Exile Currency Exchange API Preview",
        generated_at=generated_at,
        items=[
            _preview_signal_item(payload.next_change_id, market, diagnostics[market.market_id])
            for market in payload.markets
        ],
    )


def preview_currency_exchange_opportunity_inputs(
    diagnostic: CurrencyExchangeBaselineDiagnostics,
) -> OpportunityInputs | None:
    if diagnostic.confidence != "preview" or diagnostic.blockers:
        return None

    manipulation_risk = clamp_score(
        (100.0 - diagnostic.liquidity_index) * 0.5 + diagnostic.spread_index * 0.5
    )
    return OpportunityInputs(
        demand_momentum=diagnostic.demand_index,
        build_dependency_score=50.0,
        price_discount_score=50.0,
        liquidity_score=diagnostic.liquidity_index,
        historical_spike_score=50.0,
        patch_relevance_score=50.0,
        manipulation_risk=manipulation_risk,
        stale_data_penalty=diagnostic.stale_data_penalty,
    )


def _preview_signal_item(
    next_change_id: int,
    market: CurrencyExchangeMarket,
    diagnostic: CurrencyExchangeBaselineDiagnostics,
) -> ConnectorFixtureItem:
    item = currency_exchange_market_item(next_change_id, market)
    signals = preview_currency_exchange_opportunity_inputs(diagnostic)
    notes = (
        f"{item.notes}; preview baseline confidence {diagnostic.confidence}; "
        f"observations {diagnostic.observations}; freshness {diagnostic.freshness_status}"
    )
    return item.model_copy(
        update={
            "confidence": diagnostic.confidence,
            "notes": notes,
            "signals": signals,
        }
    )


__all__ = [
    "preview_currency_exchange_opportunity_inputs",
    "preview_currency_exchange_signal_fixture_from_baseline",
]
