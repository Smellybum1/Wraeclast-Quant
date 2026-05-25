from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    conditional_api_resources_text as _conditional_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_approval_patch_writes_patch_preview(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "approval.patch"

    result = runner.invoke(
        app,
        [
            "connector-approval-patch",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )
    patch_text = output_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Approval Patch Preview" in result.output
    assert "Patch available" in result.output
    assert "yes" in result.output
    assert output_path.exists()
    assert "-  allowed_use: manual-or-api-if-available" in patch_text
    assert "+  allowed_use: api" in patch_text


def test_connector_approval_patch_does_not_modify_resources(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "approval.patch"

    result = runner.invoke(
        app,
        [
            "connector-approval-patch",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert resources_path.read_text(encoding="utf-8") == original
