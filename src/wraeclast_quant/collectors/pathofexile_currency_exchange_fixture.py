from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixture,
    ConnectorFixtureItem,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def load_currency_exchange_payload(path: str | Path) -> CurrencyExchangePayload:
    fixture_path = Path(path)
    try:
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange fixture: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(f"Invalid Currency Exchange fixture JSON: {error}") from error

    try:
        return CurrencyExchangePayload.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(f"Invalid Currency Exchange fixture: {error}") from error


def load_currency_exchange_manual_snapshot(path: str | Path) -> CurrencyExchangePayload:
    snapshot_path = Path(path)
    try:
        raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange manual snapshot: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange manual snapshot JSON: {error}"
        ) from error

    try:
        snapshot = CurrencyExchangeManualSnapshot.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange manual snapshot: {error}"
        ) from error
    return currency_exchange_payload_from_manual_snapshot(snapshot)


def currency_exchange_payload_from_manual_snapshot(
    snapshot: CurrencyExchangeManualSnapshot,
) -> CurrencyExchangePayload:
    return CurrencyExchangePayload(
        next_change_id=snapshot.next_change_id,
        markets=[currency_exchange_market_from_manual_market(market) for market in snapshot.markets],
    )


def currency_exchange_market_from_manual_market(
    market: CurrencyExchangeManualMarket,
) -> CurrencyExchangeMarket:
    left = _currency_code(market.left_currency)
    right = _currency_code(market.right_currency)
    return CurrencyExchangeMarket(
        league=market.league,
        market_id=f"{left}|{right}",
        volume_traded={
            left: market.left_volume_traded,
            right: market.right_volume_traded,
        },
        lowest_stock={
            left: market.left_lowest_stock,
            right: market.right_lowest_stock,
        },
        highest_stock={
            left: market.left_highest_stock,
            right: market.right_highest_stock,
        },
        lowest_ratio={
            left: market.left_lowest_ratio,
            right: market.right_lowest_ratio,
        },
        highest_ratio={
            left: market.left_highest_ratio,
            right: market.right_highest_ratio,
        },
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


def _currency_code(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _format_mapping(values: dict[str, int]) -> str:
    return ", ".join(f"{key}={values[key]}" for key in sorted(values))


__all__ = [
    "currency_exchange_fixture_from_payload",
    "currency_exchange_market_item",
    "currency_exchange_market_from_manual_market",
    "currency_exchange_payload_from_manual_snapshot",
    "load_currency_exchange_connector_fixture",
    "load_currency_exchange_manual_snapshot",
    "load_currency_exchange_payload",
]
