from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    manual_source_resources_text as _manual_source_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_plan_invalid_review_exits_nonzero_with_blockers(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(tmp_path, _manual_source_resources_text())
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Manual Source",
        source_terms_reviewed=False,
    )

    result = runner.invoke(
        app,
        [
            "connector-plan",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Safe Fetch Plan" in result.output
    assert "not automation-eligible" in result.output
    assert "Source terms must be reviewed." in result.output
