import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import discord_resources_text as _discord_resources_text
from cli_connector_resource_text_helpers import (
    poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text,
)


runner = CliRunner()


def test_connector_review_prep_writes_draft_and_checklist(tmp_path: Path) -> None:
    resources_text = _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available")
    resources_path = _write_connector_resources(tmp_path, resources_text)
    output_dir = tmp_path / "reviews"

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    review_path = output_dir / "poe_ninja_poe2_currency_connector_review.json"
    checklist_path = output_dir / "poe_ninja_poe2_currency_review_checklist.md"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    checklist = checklist_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Review Prep" in result.output
    assert "wq connector-review-status --review-path" in result.output
    assert "wq connector-approval-helper --review-path" in result.output
    assert "wq connector-check --review-path" in result.output
    assert "wq connector-plan --review-path" in result.output
    assert review["resource_name"] == "poe.ninja POE2 Currency"
    assert review["source_terms_reviewed"] is False
    assert review["robots_or_api_policy_reviewed"] is False
    assert "Source terms URL" in checklist
    assert "Allowed data shape" in checklist
    assert resources_path.read_text(encoding="utf-8") == resources_text


def test_connector_review_prep_untouched_draft_fails_connector_check(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )
    output_dir = tmp_path / "reviews"

    prep_result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(output_dir / "poe_ninja_poe2_currency_connector_review.json"),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert prep_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output


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
