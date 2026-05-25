from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import calibration_report_args as _calibration_report_args
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)


runner = CliRunner()


def test_calibration_report_command_writes_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "calibration_report.md"
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(
        app,
        _calibration_report_args(database_path, output_path),
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote calibration report" in result.output
    assert "# Wraeclast Quant Recommendation Calibration" in report
    assert "Stormglass Catalyst" in report
    assert "Outcome Counts By Action" in report
