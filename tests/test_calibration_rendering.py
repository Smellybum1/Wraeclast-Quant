from pathlib import Path

from wraeclast_quant.commands.maintenance_calibration_rendering import (
    calibration_report_written_message,
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
