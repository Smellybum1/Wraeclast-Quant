from pathlib import Path

from wraeclast_quant.reports.calibration import write_calibration_report

from outcome_review_helpers import build_calibration_from_reviews
from outcome_review_helpers import review_record as _review


def test_write_calibration_report_creates_parent_directory(tmp_path: Path) -> None:
    output_path = write_calibration_report(
        build_calibration_from_reviews([_review()]),
        path=tmp_path / "reports" / "calibration_report.md",
    )

    assert output_path.exists()
    assert "Wraeclast Quant Recommendation Calibration" in output_path.read_text(encoding="utf-8")
