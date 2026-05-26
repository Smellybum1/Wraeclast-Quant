from wraeclast_quant.intelligence.alerts import (
    generate_alerts,
)
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities

from alert_helpers import alert_candidates as _alerts
from alert_helpers import stored_opportunity as _stored


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
