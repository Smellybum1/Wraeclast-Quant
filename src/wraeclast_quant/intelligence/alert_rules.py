from __future__ import annotations

from wraeclast_quant.intelligence.alert_models import AlertCandidate, AlertRuleSettings, _ACTION_RANK
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
    return sorted(alerts, key=_alert_sort_key)


def _alerts_for_delta(delta: OpportunityDelta, settings: AlertRuleSettings) -> list[AlertCandidate]:
    alerts: list[AlertCandidate] = []

    if _crossed_threshold(delta.previous_score, delta.latest_score, settings.buy_threshold):
        alerts.append(_candidate(delta, "high", "Score crossed into BUY"))
    elif _crossed_threshold(delta.previous_score, delta.latest_score, settings.watch_threshold):
        alerts.append(_candidate(delta, "medium", "Score crossed into WATCH"))

    if delta.status == "new" and (delta.latest_score or 0) >= settings.watch_threshold:
        alerts.append(_candidate(delta, "medium", "New WATCH-or-better item"))

    if _action_rank(delta.latest_action) > _action_rank(delta.previous_action):
        alerts.append(_candidate(delta, "medium", "Action changed upward"))

    if delta.score_delta is not None and delta.score_delta >= settings.big_positive_delta:
        alerts.append(
            _candidate(
                delta,
                "medium",
                f"Score increased by at least +{settings.big_positive_delta:.2f}",
            )
        )

    return alerts


def _candidate(delta: OpportunityDelta, severity: str, reason: str) -> AlertCandidate:
    return AlertCandidate(
        item_name=delta.item_name,
        severity=severity,
        reason=reason,
        previous_score=delta.previous_score,
        latest_score=delta.latest_score,
        score_delta=delta.score_delta,
        previous_action=delta.previous_action,
        latest_action=delta.latest_action,
    )


def _crossed_threshold(
    previous_score: float | None,
    latest_score: float | None,
    threshold: float,
) -> bool:
    if latest_score is None:
        return False
    previous = previous_score if previous_score is not None else float("-inf")
    return previous < threshold <= latest_score


def _action_rank(action: str | None) -> int:
    if action is None:
        return -1
    return _ACTION_RANK.get(action, -1)


def _alert_sort_key(alert: AlertCandidate) -> tuple[int, float, str, str]:
    severity_rank = 0 if alert.severity == "high" else 1
    score = alert.latest_score if alert.latest_score is not None else -1.0
    return (severity_rank, -score, alert.item_name, alert.reason)


__all__ = ["generate_alerts"]
