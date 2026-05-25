from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)


runner = CliRunner()


def test_connector_fixture_daily_rejects_fixture_without_signals(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            fixture_path="examples/connector_fixture_api_example.json",
            database_path=database_path,
        ),
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not database_path.exists()


def test_connector_fixture_daily_refuses_incomplete_review(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
            database_path=database_path,
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not database_path.exists()
