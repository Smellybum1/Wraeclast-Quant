from __future__ import annotations

ALLOWED_OUTCOMES = {"positive", "neutral", "negative"}


def normalize_outcome(outcome: str) -> str:
    normalized = outcome.strip().lower()
    if normalized not in ALLOWED_OUTCOMES:
        allowed = ", ".join(sorted(ALLOWED_OUTCOMES))
        raise ValueError(f"outcome must be one of: {allowed}")
    return normalized
