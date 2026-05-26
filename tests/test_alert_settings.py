import pytest
from pydantic import ValidationError

from wraeclast_quant.intelligence.alerts import AlertRuleSettings

from alert_helpers import alert_candidates as _alerts


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
