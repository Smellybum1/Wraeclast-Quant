from __future__ import annotations

from typing import Any

from wraeclast_quant.intelligence.alerts import AlertCandidate
from wraeclast_quant.intelligence.snapshot_deltas import OpportunityDelta, SnapshotComparison


def snapshot_changes_payload(
    comparison: SnapshotComparison | None,
    limit: int,
) -> dict[str, Any]:
    if comparison is None:
        return {
            "previous_run_id": None,
            "latest_run_id": None,
            "top_movers": [],
            "status_changes": [],
        }
    return {
        "previous_run_id": comparison.previous_run_id,
        "latest_run_id": comparison.latest_run_id,
        "top_movers": [delta_payload(delta) for delta in comparison.top_movers[:limit]],
        "status_changes": [delta_payload(delta) for delta in comparison.status_changes[:limit]],
    }


def delta_payload(delta: OpportunityDelta) -> dict[str, Any]:
    return {
        "item_name": delta.item_name,
        "status": delta.status,
        "previous_score": delta.previous_score,
        "latest_score": delta.latest_score,
        "score_delta": delta.score_delta,
        "previous_action": delta.previous_action,
        "latest_action": delta.latest_action,
    }


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
