from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    conditional_api_resources_text as _conditional_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


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
