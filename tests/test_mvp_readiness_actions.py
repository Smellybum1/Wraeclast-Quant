from wraeclast_quant.reports.mvp_readiness_actions import manual_observation_next_action


def test_status_manual_observation_next_action_keeps_cli_wording() -> None:
    action = manual_observation_next_action("status")

    assert action.startswith("next: prepare a local Currency Exchange manual snapshot or UI observation")
    assert "capture stock ladders first" in action
    assert "docs/MVP_DAILY_WORKFLOW.md" in action
    assert action.endswith("wq daily --input-path <manual-import-output>.")


def test_static_manual_observation_next_action_keeps_sentence_wording() -> None:
    action = manual_observation_next_action("static")

    assert action.startswith("Prepare a local Currency Exchange manual snapshot or UI observation")
    assert "capture stock ladders first" in action
    assert "docs/MVP_DAILY_WORKFLOW.md" in action
    assert action.endswith("wq daily --input-path <manual-import-output>")
