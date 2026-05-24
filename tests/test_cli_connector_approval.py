from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_resource_text_helpers import (
    conditional_api_resources_text as _conditional_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_approval_helper_prints_manual_allowed_use_suggestion(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Approval Helper" in result.output
    assert "Conditional API" in result.output
    assert "manual-or-api-if-available" in result.output
    assert "allowed_use: api" in result.output
    assert "read-only" in result.output


def test_connector_approval_helper_incomplete_review_prints_blockers_without_suggestion(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _conditional_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Conditional API",
        source_terms_url="",
    )

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Approval Helper" in result.output
    assert "source_terms_url is required" in result.output
    assert "allowed_use: api" not in result.output
    assert "None" in result.output


def test_connector_approval_helper_is_read_only(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert resources_path.read_text(encoding="utf-8") == original


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


def test_connector_review_report_invalid_review_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = tmp_path / "review.json"
    output_path = tmp_path / "review_report.md"
    review_path.write_text("{not json", encoding="utf-8")

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

    assert result.exit_code != 0
    assert "Invalid connector review JSON" in result.output
    assert not output_path.exists()


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


def test_connector_approval_patch_incomplete_review_writes_no_patch(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _conditional_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Conditional API",
        source_terms_url="",
    )
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

    assert result.exit_code == 1
    assert "Connector Approval Patch Preview" in result.output
    assert "source_terms_url is required" in result.output
    assert not output_path.exists()


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
