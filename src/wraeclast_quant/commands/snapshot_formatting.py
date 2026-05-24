from __future__ import annotations

from wraeclast_quant.intelligence.alerts import AlertCandidate


def format_score(score: float | None) -> str:
    if score is None:
        return ""
    return f"{score:.2f}"


def format_delta(delta: float | None) -> str:
    if delta is None:
        return ""
    return f"{delta:+.2f}"


def format_action_change(candidate: AlertCandidate) -> str:
    if candidate.previous_action and candidate.latest_action:
        return f"{candidate.previous_action} -> {candidate.latest_action}"
    return candidate.latest_action or candidate.previous_action or ""


__all__ = [
    "format_action_change",
    "format_delta",
    "format_score",
]
