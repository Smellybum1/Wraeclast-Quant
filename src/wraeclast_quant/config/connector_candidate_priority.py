from __future__ import annotations


def priority_rank(priority: str) -> int:
    return {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }.get(priority.strip().lower(), 4)


__all__ = ["priority_rank"]
