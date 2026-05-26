from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_diagnostics import (
    blocked_currency_exchange_baseline_diagnostic,
    currency_exchange_baseline_history,
    preview_currency_exchange_baseline_diagnostic,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
    CurrencyExchangePayload,
)


def preview_currency_exchange_rolling_baseline_diagnostics(
    payload: CurrencyExchangePayload,
    history: list[CurrencyExchangePayload],
    *,
    min_observations: int = 1,
    expected_cadence_seconds: int = 3600,
    fresh_tolerance_intervals: int = 2,
) -> dict[str, CurrencyExchangeBaselineDiagnostics]:
    baselines = currency_exchange_baseline_history(history)
    diagnostics: dict[str, CurrencyExchangeBaselineDiagnostics] = {}
    for market in payload.markets:
        current = currency_exchange_market_observation(payload.next_change_id, market)
        market_history = baselines.get((current.league, current.market_id), [])
        if len(market_history) < min_observations:
            diagnostics[current.market_id] = blocked_currency_exchange_baseline_diagnostic(
                current,
                market_history,
            )
            continue

        diagnostics[current.market_id] = preview_currency_exchange_baseline_diagnostic(
            current,
            market_history,
            current_change_id=payload.next_change_id,
            expected_cadence_seconds=expected_cadence_seconds,
            fresh_tolerance_intervals=fresh_tolerance_intervals,
        )
    return diagnostics


__all__ = ["preview_currency_exchange_rolling_baseline_diagnostics"]
