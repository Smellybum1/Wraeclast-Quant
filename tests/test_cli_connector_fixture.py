from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_connector_fixture_data_helpers import (
    write_invalid_connector_fixture as _write_invalid_connector_fixture,
)


runner = CliRunner()


def test_connector_fixture_run_prints_rows_and_count() -> None:
    result = runner.invoke(
        app,
        _connector_fixture_run_args(),
    )

    assert result.exit_code == 0
    assert "Connector Fixture Rows" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Fixture rows: 2" in result.output
    assert "Fetch plan cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_fixture_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        _connector_fixture_run_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Connector Fixture Run" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_fixture_run_invalid_fixture_exits_nonzero(tmp_path: Path) -> None:
    fixture_path = _write_invalid_connector_fixture(tmp_path)

    result = runner.invoke(
        app,
        _connector_fixture_run_args(fixture_path=fixture_path),
    )

    assert result.exit_code != 0
    assert "Invalid connector fixture" in result.output
