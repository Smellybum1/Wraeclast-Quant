from __future__ import annotations

from typing import Any


def format_score(value: Any) -> str:
    if value is None or value == "":
        return ""
    return f"{float(value):.2f}"


def format_delta(value: Any) -> str:
    if value is None or value == "":
        return ""
    return f"{float(value):+.2f}"


def format_trend_points(points: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"Run #{point.get('run_id', '')}: "
        f"{format_score(point.get('score'))} {point.get('action', '')}".strip()
        for point in points
    )


__all__ = ["format_delta", "format_score", "format_trend_points"]
