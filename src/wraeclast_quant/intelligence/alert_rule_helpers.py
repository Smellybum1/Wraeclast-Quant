from __future__ import annotations

from wraeclast_quant.intelligence.alert_models import AlertCandidate, _ACTION_RANK
from wraeclast_quant.intelligence.snapshot_deltas import OpportunityDelta


def alert_candidate(delta: OpportunityDelta, severity: str, reason: str) -> AlertCandidate:
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


def crossed_threshold(
    previous_score: float | None,
    latest_score: float | None,
    threshold: float,
) -> bool:
    if latest_score is None:
        return False
    previous = previous_score if previous_score is not None else float("-inf")
    return previous < threshold <= latest_score


def action_rank(action: str | None) -> int:
    if action is None:
        return -1
    return _ACTION_RANK.get(action, -1)


def alert_sort_key(alert: AlertCandidate) -> tuple[int, float, str, str]:
    severity_rank = 0 if alert.severity == "high" else 1
    score = alert.latest_score if alert.latest_score is not None else -1.0
    return (severity_rank, -score, alert.item_name, alert.reason)


__all__ = ["action_rank", "alert_candidate", "alert_sort_key", "crossed_threshold"]
