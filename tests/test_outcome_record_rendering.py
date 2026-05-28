from wraeclast_quant.commands.maintenance_outcome_records_rendering import (
    batch_outcome_dry_run_success_message,
    batch_outcome_record_success_message,
    batch_outcome_write_error_message,
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


def test_batch_outcome_write_error_message_says_no_records_written() -> None:
    message = batch_outcome_write_error_message(RuntimeError("blocked batch insert"))

    assert message == (
        "Error: could not record outcome batch; no records written: blocked batch insert"
    )
