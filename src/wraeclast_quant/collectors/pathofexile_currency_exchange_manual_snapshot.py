from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


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


def _currency_code(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


__all__ = [
    "currency_exchange_market_from_manual_market",
    "currency_exchange_payload_from_manual_snapshot",
    "load_currency_exchange_manual_snapshot",
]
