from __future__ import annotations

from statistics import median

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import clamp_score


def baseline_index(current_value: float, baseline_values: list[float]) -> float:
    baseline = median([max(value, 0.0) for value in baseline_values])
    if baseline <= 0:
        return 0.0
    return clamp_score((current_value / baseline) * 50.0)


def baseline_freshness(
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


def freshness_blocker(freshness_status: str) -> str:
    if freshness_status == "out-of-order":
        return "current payload predates local baseline history"
    if freshness_status == "very-stale":
        return "current payload is very stale versus local baseline cadence"
    return "current payload is stale versus local baseline cadence"


__all__ = ["baseline_freshness", "baseline_index", "freshness_blocker"]
