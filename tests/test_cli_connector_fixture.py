import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import connector_dry_run_args as _connector_dry_run_args
from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
)
from cli_connector_fixture_command_helpers import (
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_connector_fixture_data_helpers import (
    write_basic_connector_fixture as _write_basic_connector_fixture,
)
from cli_connector_fixture_data_helpers import (
    write_invalid_connector_fixture as _write_invalid_connector_fixture,
)
from cli_connector_helpers import write_connector_resources as _write_connector_resources
from cli_connector_helpers import write_connector_review as _write_connector_review


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


def test_connector_dry_run_prints_connector_class_rows_and_cache_path() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(),
    )

    assert result.exit_code == 0
    assert "Connector Dry Run" in result.output
    assert "FixtureSourceConnector" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Future cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_prints_poe_ninja_currency_connector() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            fixture_path="examples/poe_ninja_poe2_currency_fixture.json",
        ),
    )

    assert result.exit_code == 0
    assert "PoeNinjaCurrencyConnector" in result.output
    assert "poe-ninja-poe2-currency" in result.output
    assert "Exalted Orb" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output


def test_connector_dry_run_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_basic_connector_fixture(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Fixture Sources\n- name: Approved API\n  type: official\n  url: https://example.test/api\n  allowed_use: api\n",
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path=review_path,
            fixture_path=fixture_path,
            resources_path=resources_path,
        ),
    )

    assert result.exit_code == 0
    assert not Path("data/raw/cache").exists()
    assert not Path("data/wraeclast_quant.db").exists()


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
