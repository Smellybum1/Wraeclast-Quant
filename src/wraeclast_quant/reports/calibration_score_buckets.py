from __future__ import annotations


def score_bucket(score: float) -> str:
    if score >= 75.0:
        return "75+"
    if score >= 55.0:
        return "55-74.99"
    if score >= 35.0:
        return "35-54.99"
    return "<35"


__all__ = ["score_bucket"]
