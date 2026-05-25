from __future__ import annotations

from wraeclast_quant.intelligence.alerts import AlertRuleSettings, generate_alerts
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.storage.models import StoredOpportunityRecord


def alert_candidates(
    previous_score: float,
    latest_score: float,
    previous_action: str,
    latest_action: str,
    settings: AlertRuleSettings | None = None,
):
    comparison = compare_opportunities(
        previous=[stored_opportunity("Stormglass Catalyst", previous_score, previous_action)],
        latest=[stored_opportunity("Stormglass Catalyst", latest_score, latest_action)],
        previous_run_id=1,
        latest_run_id=2,
    )
    return generate_alerts(comparison, settings=settings)


def stored_opportunity(name: str, score: float, action: str) -> StoredOpportunityRecord:
    return StoredOpportunityRecord(
        id=1,
        run_id=1,
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs={
            "demand_momentum": 0,
            "build_dependency_score": 0,
            "price_discount_score": 0,
            "liquidity_score": 0,
            "historical_spike_score": 0,
            "patch_relevance_score": 0,
            "manipulation_risk": 0,
            "stale_data_penalty": 0,
        },
    )


def actual_alert_reasons() -> set[str]:
    scenarios = [
        alert_candidates(70.0, 76.0, "WATCH", "BUY"),
        alert_candidates(50.0, 56.0, "HOLD / SELL SELECTIVELY", "WATCH"),
        alert_candidates(60.0, 62.0, "WATCH", "BUY"),
        alert_candidates(20.0, 30.0, "AVOID", "AVOID"),
    ]
    comparison = compare_opportunities(
        previous=[],
        latest=[stored_opportunity("New Catalyst", 60.0, "WATCH")],
        previous_run_id=1,
        latest_run_id=2,
    )
    scenarios.append(generate_alerts(comparison))
    return {alert.reason for alerts in scenarios for alert in alerts}


__all__ = [
    "actual_alert_reasons",
    "alert_candidates",
    "stored_opportunity",
]
