from __future__ import annotations

from typing import Literal


_MANUAL_OBSERVATION_TARGET = (
    "a local Currency Exchange manual snapshot or UI observation "
    "(capture stock ladders first)"
)
_DAILY_WORKFLOW_PROMPT = (
    "follow docs/MVP_DAILY_WORKFLOW.md to create <manual-import-output> "
    "and run wq daily --input-path <manual-import-output>"
)


def manual_observation_next_action(style: Literal["status", "static"]) -> str:
    if style == "status":
        return f"next: prepare {_MANUAL_OBSERVATION_TARGET}; then {_DAILY_WORKFLOW_PROMPT}."
    return f"Prepare {_MANUAL_OBSERVATION_TARGET}, then {_DAILY_WORKFLOW_PROMPT}"


__all__ = ["manual_observation_next_action"]
