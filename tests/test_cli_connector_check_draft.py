from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)


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
