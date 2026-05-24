from __future__ import annotations

from typing import Any

from wraeclast_quant.intelligence.alerts import AlertCandidate


def alert_payload(alert: AlertCandidate) -> dict[str, Any]:
    return {
        "severity": alert.severity,
        "item_name": alert.item_name,
        "reason": alert.reason,
        "previous_score": alert.previous_score,
        "latest_score": alert.latest_score,
        "score_delta": alert.score_delta,
        "previous_action": alert.previous_action,
        "latest_action": alert.latest_action,
    }


__all__ = ["alert_payload"]
