from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)


runner = CliRunner()


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
