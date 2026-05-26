from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeMarket,
    CurrencyExchangeMarketObservation,
)


def currency_exchange_market_observation(
    next_change_id: int,
    market: CurrencyExchangeMarket,
) -> CurrencyExchangeMarketObservation:
    return CurrencyExchangeMarketObservation(
        league=market.league,
        market_id=market.market_id,
        next_change_id=next_change_id,
        volume_total=total(market.volume_traded),
        highest_stock_total=total(market.highest_stock),
        ratio_spread_percent=ratio_spread_percent(market),
    )


def total(values: dict[str, int]) -> int:
    return sum(max(value, 0) for value in values.values())


def relative_score(value: int, maximum: int) -> float:
    if maximum <= 0:
        return 0.0
    return clamp_score((value / maximum) * 100.0)


def ratio_spread_percent(market: CurrencyExchangeMarket) -> float:
    currencies = sorted(set(market.lowest_ratio) & set(market.highest_ratio))
    spreads = []
    for currency in currencies:
        low = market.lowest_ratio[currency]
        high = market.highest_ratio[currency]
        if low <= 0:
            continue
        spreads.append(((high - low) / low) * 100.0)
    if not spreads:
        return 100.0
    return clamp_score(sum(spreads) / len(spreads))


def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


__all__ = [
    "clamp_score",
    "currency_exchange_market_observation",
    "ratio_spread_percent",
    "relative_score",
    "total",
]
