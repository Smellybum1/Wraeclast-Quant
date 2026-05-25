from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)


runner = CliRunner()


def test_connector_review_status_invalid_json_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = tmp_path / "review.json"
    review_path.write_text("{not json", encoding="utf-8")

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

    assert result.exit_code != 0
    assert "Invalid connector review JSON" in result.output
