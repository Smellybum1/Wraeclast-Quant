from __future__ import annotations

from typing import Any


def latest_run_id(payload: dict[str, Any]) -> int | None:
    latest_run = payload.get("latest_run") if isinstance(payload.get("latest_run"), dict) else {}
    return _optional_int(latest_run.get("id"))


def top_opportunities_count(payload: dict[str, Any]) -> int:
    top_opportunities = payload.get("top_opportunities")
    return len(top_opportunities) if isinstance(top_opportunities, list) else 0


def alerts_count(payload: dict[str, Any]) -> int:
    alerts = payload.get("alerts")
    return len(alerts) if isinstance(alerts, list) else 0


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = ["alerts_count", "latest_run_id", "top_opportunities_count"]
