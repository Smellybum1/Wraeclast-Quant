import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_review_evidence_preserves_unrelated_fields_and_resources(
    tmp_path: Path,
) -> None:
    resources_text = _approved_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, resources_text)
    review_path = _write_connector_review(
        tmp_path,
        review_notes="Existing note.",
        rate_limit_per_minute=12,
    )

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--reviewed-at",
            "2026-05-23",
        ],
    )
    updated = json.loads(review_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert updated["review_notes"] == "Existing note."
    assert updated["rate_limit_per_minute"] == 12
    assert updated["reviewed_at"] == "2026-05-23"
    assert resources_path.read_text(encoding="utf-8") == resources_text
