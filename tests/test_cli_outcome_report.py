from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import outcome_report_args as _outcome_report_args
from cli_outcome_database_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)


runner = CliRunner()


def test_outcome_report_command_writes_markdown_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        notes="Manual review.",
    )

    result = runner.invoke(
        app,
        _outcome_report_args(database_path, output_path),
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote outcome review report" in result.output
    assert "# Wraeclast Quant Outcome Review" in report
    assert "Stormglass Catalyst" in report
    assert "Manual review." in report


def test_outcome_report_command_writes_empty_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"

    result = runner.invoke(
        app,
        _outcome_report_args(tmp_path / "snapshots.db", output_path),
    )

    assert result.exit_code == 0
    assert "Wrote empty outcome review report" in result.output
    assert "No reviewed recommendation outcomes found." in output_path.read_text(encoding="utf-8")
