from __future__ import annotations

from wraeclast_quant.intelligence.alerts import AlertRuleSettings


def create_alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    return AlertRuleSettings(
        watch_threshold=watch_threshold,
        buy_threshold=buy_threshold,
        big_positive_delta=big_delta,
    )


__all__ = ["create_alert_settings"]
