from pathlib import Path

from wraeclast_quant.commands.maintenance_calibration_rendering import (
    calibration_local_readonly_message,
    calibration_report_written_message,
    calibration_report_next_action,
)


def test_calibration_report_written_message_for_reviewed_report() -> None:
    path = Path("calibration_report.md")

    assert (
        calibration_report_written_message(
            path,
            has_outcomes=True,
        )
        == f"Wrote calibration report to {path}"
    )


def test_calibration_report_written_message_for_empty_report() -> None:
    path = Path("calibration_report.md")

    assert (
        calibration_report_written_message(
            path,
            has_outcomes=False,
        )
        == f"Wrote empty calibration report to {path}"
    )


def test_calibration_local_readonly_message_preserves_cli_text() -> None:
    assert calibration_local_readonly_message() == (
        "Calibration is local-only and read-only. "
        "It did not change scoring weights or thresholds."
    )


def test_calibration_report_next_action_preserves_cli_text() -> None:
    assert calibration_report_next_action() == (
        "Next: run wq calibration-report --output-path "
        "data/processed/calibration_report.md to write the local Markdown calibration artifact."
    )
