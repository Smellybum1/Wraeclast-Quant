from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
    CurrencyExchangeMarket,
    CurrencyExchangePayload,
)


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
    left = currency_exchange_manual_currency_code(market.left_currency)
    right = currency_exchange_manual_currency_code(market.right_currency)
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


def currency_exchange_manual_currency_code(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


__all__ = [
    "currency_exchange_manual_currency_code",
    "currency_exchange_market_from_manual_market",
    "currency_exchange_payload_from_manual_snapshot",
]
