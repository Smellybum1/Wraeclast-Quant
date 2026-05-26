from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_review_status_incomplete_review_exits_zero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = tmp_path / "draft.json"
    draft_result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "approved_api",
            "--access-method",
            "api",
            "--output-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )
    status_result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert status_result.exit_code == 0
    assert "Connector Review Status" in status_result.output
    assert "Approved API" in status_result.output
    assert "Source terms URL" in status_result.output
    assert "Robots/API policy URL" in status_result.output
    assert "Allowed data shape" in status_result.output
    assert "not ready" in status_result.output
    assert "Source terms must be reviewed." in status_result.output
    assert "Robots.txt or API policy must be reviewed." in status_result.output


def test_connector_review_status_marks_missing_claimed_evidence_blocked(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        allowed_data_shape="",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Status" in result.output
    assert "Source terms URL" in result.output
    assert "blocked" in result.output
    assert "source_terms_url is required" in result.output
