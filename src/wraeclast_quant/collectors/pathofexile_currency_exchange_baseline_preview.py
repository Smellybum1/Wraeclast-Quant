from __future__ import annotations

from statistics import median

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    clamp_score,
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

        volume_index = _baseline_index(
            current.volume_total,
            [observation.volume_total for observation in market_history],
        )
        stock_index = _baseline_index(
            current.highest_stock_total,
            [observation.highest_stock_total for observation in market_history],
        )
        spread_index = _baseline_index(
            current.ratio_spread_percent,
            [observation.ratio_spread_percent for observation in market_history],
        )
        latest_history_change_id = max(observation.next_change_id for observation in market_history)
        freshness_lag_seconds, freshness_status, stale_data_penalty = _baseline_freshness(
            payload.next_change_id,
            latest_history_change_id,
            expected_cadence_seconds=expected_cadence_seconds,
            fresh_tolerance_intervals=fresh_tolerance_intervals,
        )
        if stale_data_penalty:
            blockers.append(_freshness_blocker(freshness_status))

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


def _baseline_index(current_value: float, baseline_values: list[float]) -> float:
    baseline = median([max(value, 0.0) for value in baseline_values])
    if baseline <= 0:
        return 0.0
    return clamp_score((current_value / baseline) * 50.0)


def _baseline_freshness(
    current_next_change_id: int,
    latest_history_change_id: int,
    *,
    expected_cadence_seconds: int,
    fresh_tolerance_intervals: int,
) -> tuple[int, str, float]:
    cadence = max(expected_cadence_seconds, 1)
    tolerance = cadence * max(fresh_tolerance_intervals, 1)
    lag_seconds = current_next_change_id - latest_history_change_id
    if lag_seconds < 0:
        return lag_seconds, "out-of-order", 40.0
    if lag_seconds <= tolerance:
        return lag_seconds, "fresh", 0.0
    if lag_seconds <= tolerance * 2:
        return lag_seconds, "stale", 20.0
    return lag_seconds, "very-stale", 40.0


def _freshness_blocker(freshness_status: str) -> str:
    if freshness_status == "out-of-order":
        return "current payload predates local baseline history"
    if freshness_status == "very-stale":
        return "current payload is very stale versus local baseline cadence"
    return "current payload is stale versus local baseline cadence"


__all__ = ["preview_currency_exchange_rolling_baseline_diagnostics"]
