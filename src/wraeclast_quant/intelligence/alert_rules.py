from __future__ import annotations

from wraeclast_quant.intelligence.alert_models import AlertCandidate, AlertRuleSettings
from wraeclast_quant.intelligence.alert_rule_helpers import (
    action_rank,
    alert_candidate,
    alert_sort_key,
    crossed_threshold,
)
from wraeclast_quant.intelligence.snapshot_deltas import OpportunityDelta, SnapshotComparison


def generate_alerts(
    comparison: SnapshotComparison,
    settings: AlertRuleSettings | None = None,
) -> list[AlertCandidate]:
    alert_settings = settings or AlertRuleSettings()
    alerts: list[AlertCandidate] = []
    seen_reasons: set[tuple[str, str]] = set()
    for delta in comparison.deltas:
        for alert in _alerts_for_delta(delta, alert_settings):
            key = (alert.item_name, alert.reason)
            if key in seen_reasons:
                continue
            seen_reasons.add(key)
            alerts.append(alert)
    return sorted(alerts, key=alert_sort_key)


def _alerts_for_delta(delta: OpportunityDelta, settings: AlertRuleSettings) -> list[AlertCandidate]:
    alerts: list[AlertCandidate] = []

    if crossed_threshold(delta.previous_score, delta.latest_score, settings.buy_threshold):
        alerts.append(alert_candidate(delta, "high", "Score crossed into BUY"))
    elif crossed_threshold(delta.previous_score, delta.latest_score, settings.watch_threshold):
        alerts.append(alert_candidate(delta, "medium", "Score crossed into WATCH"))

    if delta.status == "new" and (delta.latest_score or 0) >= settings.watch_threshold:
        alerts.append(alert_candidate(delta, "medium", "New WATCH-or-better item"))

    if action_rank(delta.latest_action) > action_rank(delta.previous_action):
        alerts.append(alert_candidate(delta, "medium", "Action changed upward"))

    if delta.score_delta is not None and delta.score_delta >= settings.big_positive_delta:
        alerts.append(
            alert_candidate(
                delta,
                "medium",
                f"Score increased by at least +{settings.big_positive_delta:.2f}",
            )
        )

    return alerts


__all__ = ["generate_alerts"]
