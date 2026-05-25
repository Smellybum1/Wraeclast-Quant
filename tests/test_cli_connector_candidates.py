from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import discord_resources_text as _discord_resources_text
from cli_connector_resource_text_helpers import (
    poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text,
)


runner = CliRunner()


def test_connector_candidates_prints_candidate_rows_and_draft_commands(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(
            allowed_use="manual-or-api-if-available",
            include_manual_source=True,
        ),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Connector Review Candidates" in result.output
    assert "poe.ninja POE2 Currency" in result.output
    assert "price_site" in result.output
    assert "needs-review" in result.output
    assert "wq connector-draft" in result.output
    assert "--resource poe_ninja_poe2_currency" in result.output
    assert "--access-method api" in result.output
    assert "advisory only" in result.output


def test_connector_candidates_marks_discord_as_compliance_gated(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Official Discord" in result.output
    assert "discord-gated" in result.output
    assert "Compliance-gated" in result.output


def test_connector_candidates_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert not (tmp_path / "examples").exists()
    assert not (tmp_path / "data").exists()
