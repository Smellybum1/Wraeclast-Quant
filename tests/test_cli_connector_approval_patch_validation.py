from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    conditional_api_resources_text as _conditional_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_approval_patch_incomplete_review_writes_no_patch(
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
