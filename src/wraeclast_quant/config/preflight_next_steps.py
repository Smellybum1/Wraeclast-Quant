from __future__ import annotations


def fallback_next_step(status: str) -> str:
    if status == "blocked":
        return "Do not automate this source."
    if status == "manual-review":
        return "Keep this source manual-review only."
    return "Clarify allowed use and review source terms before connector work."


__all__ = ["fallback_next_step"]
