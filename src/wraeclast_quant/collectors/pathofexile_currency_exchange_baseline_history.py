from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeMarketObservation,
    CurrencyExchangePayload,
)

BaselineHistory = dict[tuple[str, str], list[CurrencyExchangeMarketObservation]]


def currency_exchange_baseline_history(
    history: list[CurrencyExchangePayload],
) -> BaselineHistory:
    baselines: BaselineHistory = {}
    for history_payload in history:
        for market in history_payload.markets:
            observation = currency_exchange_market_observation(history_payload.next_change_id, market)
            baselines.setdefault((observation.league, observation.market_id), []).append(observation)
    return baselines


__all__ = [
    "BaselineHistory",
    "currency_exchange_baseline_history",
]
