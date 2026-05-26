from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_metrics import (
    baseline_freshness,
    baseline_index,
    freshness_blocker,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
    CurrencyExchangeMarketObservation,
)


def blocked_currency_exchange_baseline_diagnostic(
    current: CurrencyExchangeMarketObservation,
    market_history: list[CurrencyExchangeMarketObservation],
) -> CurrencyExchangeBaselineDiagnostics:
    return CurrencyExchangeBaselineDiagnostics(
        league=current.league,
        market_id=current.market_id,
        observations=len(market_history),
        demand_index=0.0,
        liquidity_index=0.0,
        spread_index=0.0,
        freshness_lag_seconds=0,
        freshness_status="missing-history",
        stale_data_penalty=20.0,
        confidence="blocked",
        blockers=("insufficient local baseline history",),
    )


def preview_currency_exchange_baseline_diagnostic(
    current: CurrencyExchangeMarketObservation,
    market_history: list[CurrencyExchangeMarketObservation],
    *,
    current_change_id: int,
    expected_cadence_seconds: int,
    fresh_tolerance_intervals: int,
) -> CurrencyExchangeBaselineDiagnostics:
    volume_index = baseline_index(
        current.volume_total,
        [observation.volume_total for observation in market_history],
    )
    stock_index = baseline_index(
        current.highest_stock_total,
        [observation.highest_stock_total for observation in market_history],
    )
    spread_index = baseline_index(
        current.ratio_spread_percent,
        [observation.ratio_spread_percent for observation in market_history],
    )
    latest_history_change_id = max(observation.next_change_id for observation in market_history)
    freshness_lag_seconds, freshness_status, stale_data_penalty = baseline_freshness(
        current_change_id,
        latest_history_change_id,
        expected_cadence_seconds=expected_cadence_seconds,
        fresh_tolerance_intervals=fresh_tolerance_intervals,
    )
    blockers = (freshness_blocker(freshness_status),) if stale_data_penalty else ()

    return CurrencyExchangeBaselineDiagnostics(
        league=current.league,
        market_id=current.market_id,
        observations=len(market_history),
        demand_index=volume_index,
        liquidity_index=round(volume_index * 0.7 + stock_index * 0.3, 2),
        spread_index=spread_index,
        freshness_lag_seconds=freshness_lag_seconds,
        freshness_status=freshness_status,
        stale_data_penalty=stale_data_penalty,
        confidence="preview" if not blockers else "warning",
        blockers=blockers,
    )


__all__ = [
    "blocked_currency_exchange_baseline_diagnostic",
    "preview_currency_exchange_baseline_diagnostic",
]
