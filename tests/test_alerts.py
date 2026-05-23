from pathlib import Path

import pytest
from pydantic import ValidationError

from wraeclast_quant.intelligence.alerts import (
    BIG_POSITIVE_DELTA,
    BUY_THRESHOLD,
    WATCH_THRESHOLD,
    AlertRuleSettings,
    generate_alerts,
)
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.storage.models import StoredOpportunityRecord


def test_buy_crossing_creates_high_alert() -> None:
    alerts = _alerts(previous_score=70.0, latest_score=76.0, previous_action="WATCH", latest_action="BUY")

    assert any(alert.reason == "Score crossed into BUY" for alert in alerts)
    assert next(alert for alert in alerts if alert.reason == "Score crossed into BUY").severity == "high"


def test_watch_crossing_creates_alert() -> None:
    alerts = _alerts(
        previous_score=50.0,
        latest_score=56.0,
        previous_action="HOLD / SELL SELECTIVELY",
        latest_action="WATCH",
    )

    assert any(alert.reason == "Score crossed into WATCH" for alert in alerts)


def test_upward_action_change_creates_alert() -> None:
    alerts = _alerts(previous_score=60.0, latest_score=62.0, previous_action="WATCH", latest_action="BUY")

    assert any(alert.reason == "Action changed upward" for alert in alerts)


def test_new_watch_or_better_item_creates_alert() -> None:
    comparison = compare_opportunities(
        previous=[],
        latest=[_stored("New Catalyst", 60.0, "WATCH")],
        previous_run_id=1,
        latest_run_id=2,
    )

    alerts = generate_alerts(comparison)

    assert any(alert.reason == "New WATCH-or-better item" for alert in alerts)
    assert any(alert.item_name == "New Catalyst" for alert in alerts)


def test_big_positive_delta_creates_alert() -> None:
    alerts = _alerts(previous_score=20.0, latest_score=30.0, previous_action="AVOID", latest_action="AVOID")

    assert any(alert.reason == "Score increased by at least +10.00" for alert in alerts)


def test_stable_comparison_creates_no_alerts() -> None:
    alerts = _alerts(previous_score=70.0, latest_score=70.0, previous_action="WATCH", latest_action="WATCH")

    assert alerts == []


def test_lower_watch_threshold_creates_watch_crossing_alert() -> None:
    alerts = _alerts(
        previous_score=45.0,
        latest_score=51.0,
        previous_action="HOLD / SELL SELECTIVELY",
        latest_action="WATCH",
        settings=AlertRuleSettings(watch_threshold=50.0),
    )

    assert any(alert.reason == "Score crossed into WATCH" for alert in alerts)


def test_higher_big_delta_suppresses_delta_alert() -> None:
    alerts = _alerts(
        previous_score=20.0,
        latest_score=30.0,
        previous_action="AVOID",
        latest_action="AVOID",
        settings=AlertRuleSettings(big_positive_delta=20.0),
    )

    assert not any(alert.reason == "Score increased by at least +10.00" for alert in alerts)


def test_invalid_threshold_order_is_rejected() -> None:
    with pytest.raises(ValidationError, match="buy_threshold"):
        AlertRuleSettings(watch_threshold=80.0, buy_threshold=70.0)


def test_alert_rules_contract_doc_matches_defaults_and_reasons() -> None:
    doc_text = Path("docs/ALERTS.md").read_text(encoding="utf-8")
    documented_settings = _documented_mapping(doc_text, "Default alert settings:")
    documented_reasons = _documented_bullets(doc_text, "Alert reasons:")

    assert documented_settings == {
        "watch_threshold": str(WATCH_THRESHOLD),
        "buy_threshold": str(BUY_THRESHOLD),
        "big_positive_delta": str(BIG_POSITIVE_DELTA),
    }
    assert documented_reasons == {
        "Score crossed into BUY",
        "Score crossed into WATCH",
        "New WATCH-or-better item",
        "Action changed upward",
        "Score increased by at least +<big_positive_delta>",
    }
    assert _actual_alert_reasons() == {
        "Score crossed into BUY",
        "Score crossed into WATCH",
        "New WATCH-or-better item",
        "Action changed upward",
        f"Score increased by at least +{BIG_POSITIVE_DELTA:.2f}",
    }


def _alerts(
    previous_score: float,
    latest_score: float,
    previous_action: str,
    latest_action: str,
    settings: AlertRuleSettings | None = None,
):
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", previous_score, previous_action)],
        latest=[_stored("Stormglass Catalyst", latest_score, latest_action)],
        previous_run_id=1,
        latest_run_id=2,
    )
    return generate_alerts(comparison, settings=settings)


def _stored(name: str, score: float, action: str) -> StoredOpportunityRecord:
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


def _actual_alert_reasons() -> set[str]:
    scenarios = [
        _alerts(70.0, 76.0, "WATCH", "BUY"),
        _alerts(50.0, 56.0, "HOLD / SELL SELECTIVELY", "WATCH"),
        _alerts(60.0, 62.0, "WATCH", "BUY"),
        _alerts(20.0, 30.0, "AVOID", "AVOID"),
    ]
    comparison = compare_opportunities(
        previous=[],
        latest=[_stored("New Catalyst", 60.0, "WATCH")],
        previous_run_id=1,
        latest_run_id=2,
    )
    scenarios.append(generate_alerts(comparison))
    return {alert.reason for alerts in scenarios for alert in alerts}


def _documented_mapping(doc_text: str, heading: str) -> dict[str, str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        key.strip("`"): value.strip("`")
        for key, value in (
            line.strip()[2:].split(": ", 1)
            for line in section.splitlines()
            if line.strip().startswith("- `")
        )
    }


def _documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }
