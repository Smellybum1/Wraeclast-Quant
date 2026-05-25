from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_plan_does_not_create_cache_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(tmp_path)

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

    assert result.exit_code == 0
    assert not Path("data/raw/cache").exists()
