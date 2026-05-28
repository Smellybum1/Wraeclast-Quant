from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row


def add_calibration_prompt_row(
    status_rows: list[dict[str, str]],
    context: StatusHealthContext,
) -> None:
    add_status_row(
        status_rows,
        "Calibration prompts",
        calibration_prompt_status(context),
        calibration_prompt_details(context),
    )


def calibration_prompt_status(context: StatusHealthContext) -> str:
    if context.latest is None or context.coverage is None:
        return "none"
    return "ok"


def calibration_prompt_details(context: StatusHealthContext) -> str:
    if context.latest is None:
        return "No local run yet; record reviewed outcomes before calibration prompts."
    if context.coverage is None or context.coverage.reviewed_recommendations == 0:
        return f"No reviewed outcomes for run #{context.latest.id}; next: wq review-coverage --run-id {context.latest.id}."
    if not context.calibration_prompts:
        return "No calibration review prompts triggered; scoring unchanged."
    count = len(context.calibration_prompts)
    return (
        f"{count} local read-only prompt(s); next: wq calibration. "
        "Prompts do not retune scoring or change recommendations."
    )


__all__ = [
    "add_calibration_prompt_row",
    "calibration_prompt_details",
    "calibration_prompt_status",
]
