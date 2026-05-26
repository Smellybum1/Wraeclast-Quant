from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_market_text import (
    currency_exchange_currency_label,
    currency_exchange_market_pair,
    format_currency_exchange_mapping,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_payload_loader import (
    load_currency_exchange_payload,
)
from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixture,
    ConnectorFixtureItem,
)


def currency_exchange_fixture_from_payload(
    payload: CurrencyExchangePayload,
) -> ConnectorFixture:
    generated_at = datetime.fromtimestamp(payload.next_change_id, tz=UTC).isoformat()
    return ConnectorFixture(
        source_name="Path of Exile Currency Exchange API",
        generated_at=generated_at,
        items=[currency_exchange_market_item(payload.next_change_id, market) for market in payload.markets],
    )


def currency_exchange_market_item(
    next_change_id: int,
    market: CurrencyExchangeMarket,
) -> ConnectorFixtureItem:
    left, right = currency_exchange_market_pair(market.market_id)
    name = f"{currency_exchange_currency_label(left)} / {currency_exchange_currency_label(right)}"
    return ConnectorFixtureItem(
        name=name,
        category="currency",
        confidence="medium",
        price_text=(
            f"hourly aggregate {market.market_id}; "
            f"lowest ratio {format_currency_exchange_mapping(market.lowest_ratio)}; "
            f"highest ratio {format_currency_exchange_mapping(market.highest_ratio)}"
        ),
        notes=(
            f"Official Currency Exchange historical hour {next_change_id}; "
            f"league {market.league}; "
            f"volume {format_currency_exchange_mapping(market.volume_traded)}; "
            f"stock {format_currency_exchange_mapping(market.lowest_stock)} "
            f"to {format_currency_exchange_mapping(market.highest_stock)}"
        ),
    )


def load_currency_exchange_connector_fixture(path: str | Path) -> ConnectorFixture:
    return currency_exchange_fixture_from_payload(load_currency_exchange_payload(path))


__all__ = [
    "currency_exchange_fixture_from_payload",
    "currency_exchange_market_item",
    "load_currency_exchange_connector_fixture",
]
