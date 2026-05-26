from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_metrics import (
    baseline_freshness,
    baseline_index,
    freshness_blocker,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
    CurrencyExchangeMarketObservation,
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
    baselines: dict[tuple[str, str], list[CurrencyExchangeMarketObservation]] = {}
    for history_payload in history:
        for market in history_payload.markets:
            observation = currency_exchange_market_observation(history_payload.next_change_id, market)
            baselines.setdefault((observation.league, observation.market_id), []).append(observation)

    diagnostics: dict[str, CurrencyExchangeBaselineDiagnostics] = {}
    for market in payload.markets:
        current = currency_exchange_market_observation(payload.next_change_id, market)
        market_history = baselines.get((current.league, current.market_id), [])
        blockers: list[str] = []
        if len(market_history) < min_observations:
            blockers.append("insufficient local baseline history")
            diagnostics[current.market_id] = CurrencyExchangeBaselineDiagnostics(
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
                blockers=tuple(blockers),
            )
            continue

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
            payload.next_change_id,
            latest_history_change_id,
            expected_cadence_seconds=expected_cadence_seconds,
            fresh_tolerance_intervals=fresh_tolerance_intervals,
        )
        if stale_data_penalty:
            blockers.append(freshness_blocker(freshness_status))

        diagnostics[current.market_id] = CurrencyExchangeBaselineDiagnostics(
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
            blockers=tuple(blockers),
        )
    return diagnostics


__all__ = ["preview_currency_exchange_rolling_baseline_diagnostics"]
