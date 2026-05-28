from wraeclast_quant.commands.intake_watchlist_rendering import (
    calibration_prompt_next_action,
)


def test_calibration_prompt_next_action_is_read_only() -> None:
    assert calibration_prompt_next_action(2) == (
        "Calibration prompts: 2 local read-only prompt(s). "
        "Next: wq calibration. Prompts do not retune scoring or change recommendations."
    )
