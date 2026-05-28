from wraeclast_quant.commands.maintenance_outcome_records_rendering import (
    batch_outcome_dry_run_success_message,
    batch_outcome_record_success_message,
    batch_outcome_validation_error_message,
    batch_outcome_write_error_message,
    no_outcomes_message,
    recent_outcomes_next_action,
)


def test_batch_outcome_dry_run_success_message_points_to_final_record_command() -> None:
    message = batch_outcome_dry_run_success_message(
        6,
        13,
        "data/processed/outcome_decisions.json",
    )

    assert message == "\n".join(
        [
            "Validated 6 outcome decision(s) for run #13 "
            "from data/processed/outcome_decisions.json; no records written.",
            "Next: wq record-outcomes --input-path data/processed/outcome_decisions.json",
        ]
    )


def test_batch_outcome_record_success_message_preserves_cli_text() -> None:
    assert (
        batch_outcome_record_success_message(
            6,
            13,
            "data/processed/outcome_decisions.json",
        )
        == "Recorded 6 outcome(s) for run #13 from data/processed/outcome_decisions.json."
    )


def test_batch_outcome_validation_error_message_says_no_records_written() -> None:
    message = batch_outcome_validation_error_message(
        ValueError("item 'Missing Item' was not found in analysis run #13")
    )

    assert message == (
        "Error: could not validate outcome batch; no records written: "
        "item 'Missing Item' was not found in analysis run #13"
    )


def test_batch_outcome_write_error_message_says_no_records_written() -> None:
    message = batch_outcome_write_error_message(RuntimeError("blocked batch insert"))

    assert message == (
        "Error: could not record outcome batch; no records written: blocked batch insert"
    )


def test_recent_outcomes_next_action_points_to_review_and_calibration() -> None:
    assert recent_outcomes_next_action() == (
        "Next: run wq outcome-review to inspect scores/actions with outcomes, "
        "or wq calibration to summarize reviewed recommendations."
    )


def test_no_outcomes_message_preserves_empty_state_text() -> None:
    assert no_outcomes_message() == "No recommendation outcomes recorded."
