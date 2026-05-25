import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
)


runner = CliRunner()


def test_connector_fixture_export_writes_manual_import_json(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(output_path=output_path),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Connector Fixture Export" in result.output
    assert "2" in result.output
    assert str(output_path) in result.output
    assert payload["items"][0]["name"] == "Stormglass Catalyst"
    assert "signals" in payload["items"][0]


def test_connector_fixture_export_rejects_fixture_without_signals(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(
            output_path=output_path,
            fixture_path="examples/connector_fixture_api_example.json",
        ),
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not output_path.exists()


def test_connector_fixture_export_refuses_incomplete_review(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(
            output_path=output_path,
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not output_path.exists()
