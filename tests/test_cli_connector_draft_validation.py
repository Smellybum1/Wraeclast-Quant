from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_resource_text_helpers import discord_resources_text as _discord_resources_text


runner = CliRunner()


def test_connector_draft_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Missing API",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource found" in result.output
    assert not output_path.exists()


def test_connector_draft_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output
    assert not output_path.exists()
