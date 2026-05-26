from __future__ import annotations

from datetime import UTC, datetime

from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_preview import (
    preview_currency_exchange_rolling_baseline_diagnostics,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_fixture import (
    currency_exchange_market_item,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_opportunity_preview import (
    preview_currency_exchange_opportunity_inputs,
)
from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixture,
    ConnectorFixtureItem,
)


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
            preview_currency_exchange_signal_item(
                payload.next_change_id,
                market,
                diagnostics[market.market_id],
            )
            for market in payload.markets
        ],
    )


def preview_currency_exchange_signal_item(
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
    "preview_currency_exchange_signal_fixture_from_baseline",
    "preview_currency_exchange_signal_item",
]
