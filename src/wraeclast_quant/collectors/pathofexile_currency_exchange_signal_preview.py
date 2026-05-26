from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    clamp_score,
    ratio_spread_percent,
    relative_score,
    total,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangePayload,
)
from wraeclast_quant.intelligence.scoring import OpportunityInputs


def preview_currency_exchange_signal_inputs(
    payload: CurrencyExchangePayload,
) -> dict[str, OpportunityInputs]:
    max_volume = max((total(market.volume_traded) for market in payload.markets), default=0)
    max_stock = max((total(market.highest_stock) for market in payload.markets), default=0)

    signals: dict[str, OpportunityInputs] = {}
    for market in payload.markets:
        volume_score = relative_score(total(market.volume_traded), max_volume)
        stock_score = relative_score(total(market.highest_stock), max_stock)
        liquidity_score = round(volume_score * 0.7 + stock_score * 0.3, 2)
        spread_percent = ratio_spread_percent(market)
        manipulation_risk = clamp_score((100.0 - liquidity_score) * 0.6 + spread_percent * 0.4)
        signals[market.market_id] = OpportunityInputs(
            demand_momentum=volume_score,
            build_dependency_score=50.0,
            price_discount_score=50.0,
            liquidity_score=liquidity_score,
            historical_spike_score=50.0,
            patch_relevance_score=50.0,
            manipulation_risk=manipulation_risk,
            stale_data_penalty=20.0,
        )
    return signals


__all__ = ["preview_currency_exchange_signal_inputs"]
