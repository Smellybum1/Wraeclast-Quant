from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    conditional_api_resources_text as _conditional_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_review_report_writes_markdown(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "review_report.md"

    result = runner.invoke(
        app,
        [
            "connector-review-report",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )
    markdown = output_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Review Report" in result.output
    assert "Conditional API" in result.output
    assert "allowed_use: api" in result.output
    assert output_path.exists()
    assert "# Connector Review Report: Conditional API" in markdown
    assert "Current allowed_use: `manual-or-api-if-available`" in markdown
    assert "Approval suggestion: `allowed_use: api`" in markdown
    assert "Connector-check readiness: `not ready`" in markdown


def test_connector_review_report_is_read_only_for_resources(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "review_report.md"

    result = runner.invoke(
        app,
        [
            "connector-review-report",
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
