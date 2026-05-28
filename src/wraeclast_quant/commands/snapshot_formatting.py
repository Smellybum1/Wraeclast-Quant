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


def hidden_snapshot_items_text(
    *,
    displayed_count: int,
    total_count: int,
    max_limit: int = 25,
) -> str | None:
    if total_count <= displayed_count:
        return None
    next_limit = min(total_count, max_limit)
    detail = "all" if next_limit == total_count else "more"
    return (
        f"Showing top {displayed_count} of {total_count} scored opportunities. "
        f"Re-run with --limit {next_limit} to show {detail}."
    )


__all__ = [
    "format_action_change",
    "format_delta",
    "format_score",
    "hidden_snapshot_items_text",
]
