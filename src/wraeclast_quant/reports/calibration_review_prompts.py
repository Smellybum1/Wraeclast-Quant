from __future__ import annotations

from wraeclast_quant.reports.calibration_models import CalibrationResult


def calibration_review_prompts(result: CalibrationResult) -> list[str]:
    prompts: list[str] = []
    avoid_positives = result.by_action.get("AVOID", {}).get("positive", 0)
    if avoid_positives:
        prompts.append(
            f"AVOID has {avoid_positives} positive outcome(s); "
            "inspect low-score signal coverage before changing scoring."
        )

    higher_action_negative_prompts = _higher_action_negative_prompts(result)
    prompts.extend(higher_action_negative_prompts)

    positive_average = result.average_score_by_outcome.get("positive")
    neutral_average = result.average_score_by_outcome.get("neutral")
    if positive_average is not None and neutral_average is not None and positive_average < neutral_average:
        prompts.append(
            f"Positive outcomes average {positive_average:.2f}, below neutral average "
            f"{neutral_average:.2f}; review score buckets before tuning thresholds."
        )
    return prompts


def _higher_action_negative_prompts(result: CalibrationResult) -> list[str]:
    prompts: list[str] = []
    for action in ("BUY", "WATCH", "HOLD / SELL SELECTIVELY"):
        negatives = result.by_action.get(action, {}).get("negative", 0)
        if negatives:
            prompts.append(
                f"{action} has {negatives} negative outcome(s); "
                "inspect stale inputs or threshold behavior before changing scoring."
            )
    return prompts


def calibration_review_prompt_lines(result: CalibrationResult) -> list[str]:
    prompts = calibration_review_prompts(result)
    if not prompts:
        return ["No calibration review prompts triggered."]
    return [f"- {prompt}" for prompt in prompts]


def calibration_review_prompt_caveat() -> str:
    return (
        "Review prompts are local-only and read-only. "
        "They do not retune scoring or change recommendations."
    )


__all__ = [
    "calibration_review_prompt_caveat",
    "calibration_review_prompt_lines",
    "calibration_review_prompts",
]
