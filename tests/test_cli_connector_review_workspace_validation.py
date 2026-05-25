from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import discord_resources_text as _discord_resources_text


runner = CliRunner()


def test_connector_review_prep_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Price Data\n- name: Manual Source\n  allowed_use: manual-review\n",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "missing",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource" in result.output


def test_connector_review_prep_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output
