from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_resource_text_helpers import (
    manual_source_resources_text as _manual_source_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_check_on_untouched_draft_exits_nonzero(tmp_path: Path) -> None:
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
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output
    assert "Robots.txt or API policy must be reviewed." in check_result.output


def test_connector_check_invalid_review_exits_nonzero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _manual_source_resources_text())
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Manual Source",
        source_terms_reviewed=False,
    )

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "Manual Source" in result.output
    assert "not automation-eligible" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_check_missing_claimed_evidence_exits_nonzero(tmp_path: Path) -> None:
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
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "source_terms_url is required" in result.output
    assert "robots_or_api_policy_url is required" in result.output
    assert "reviewed_at is required" in result.output
    assert "allowed_data_shape is required" in result.output
