from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_outcome_command_helpers import outcomes_args as _outcomes_args
from cli_outcome_database_helpers import (
    fully_reviewed_calibration_prompt_database as _fully_reviewed_calibration_prompt_database,
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)


runner = CliRunner()


def test_outcomes_command_prints_recent_outcomes_and_summary(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(app, _outcomes_args(database_path))

    assert result.exit_code == 0
    assert "Recommendation Outcomes" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Outcome Summary" in result.output
    assert "positive" in result.output
    assert "wq outcome-review" in result.output
    assert "wq calibration" in result.output


def test_outcomes_command_points_prompt_patterns_to_calibration(tmp_path: Path) -> None:
    database_path, _run = _fully_reviewed_calibration_prompt_database(tmp_path)

    result = runner.invoke(app, _outcomes_args(database_path))

    assert result.exit_code == 0
    assert "Calibration prompts: 2 local read-only prompt(s)." in result.output
    assert "Next: wq calibration" in result.output
    assert "do not retune scoring or change recommendations" in result.output


def test_outcomes_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _outcomes_args(tmp_path / "snapshots.db"),
    )

    assert result.exit_code == 0
    assert "No recommendation outcomes recorded." in result.output
