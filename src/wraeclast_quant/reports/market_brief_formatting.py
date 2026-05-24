from __future__ import annotations


def format_score(score: float | None) -> str:
    if score is None:
        return ""
    return f"{score:.2f}"


def format_delta(delta: float | None) -> str:
    if delta is None:
        return ""
    return f"{delta:+.2f}"


__all__ = ["format_delta", "format_score"]
