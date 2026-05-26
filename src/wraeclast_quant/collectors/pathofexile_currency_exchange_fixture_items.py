from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_payload_loader import (
    load_currency_exchange_payload,
)
from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixture,
    ConnectorFixtureItem,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


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
    left, right = _market_pair(market.market_id)
    name = f"{_currency_label(left)} / {_currency_label(right)}"
    return ConnectorFixtureItem(
        name=name,
        category="currency",
        confidence="medium",
        price_text=(
            f"hourly aggregate {market.market_id}; "
            f"lowest ratio {_format_mapping(market.lowest_ratio)}; "
            f"highest ratio {_format_mapping(market.highest_ratio)}"
        ),
        notes=(
            f"Official Currency Exchange historical hour {next_change_id}; "
            f"league {market.league}; "
            f"volume {_format_mapping(market.volume_traded)}; "
            f"stock {_format_mapping(market.lowest_stock)} to {_format_mapping(market.highest_stock)}"
        ),
    )


def load_currency_exchange_connector_fixture(path: str | Path) -> ConnectorFixture:
    return currency_exchange_fixture_from_payload(load_currency_exchange_payload(path))


def _market_pair(market_id: str) -> tuple[str, str]:
    parts = [part.strip() for part in market_id.split("|")]
    if len(parts) != 2 or not all(parts):
        raise ConnectorPolicyError(
            "Currency Exchange market_id must contain two currency codes separated by '|'."
        )
    return parts[0], parts[1]


def _currency_label(code: str) -> str:
    labels = {
        "chaos": "Chaos Orb",
        "divine": "Divine Orb",
        "exalted": "Exalted Orb",
        "regal": "Regal Orb",
    }
    return labels.get(code, code.replace("_", " ").title())


def _format_mapping(values: dict[str, int]) -> str:
    return ", ".join(f"{key}={values[key]}" for key in sorted(values))


__all__ = [
    "currency_exchange_fixture_from_payload",
    "currency_exchange_market_item",
    "load_currency_exchange_connector_fixture",
]
