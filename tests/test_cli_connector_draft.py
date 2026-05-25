from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.config.connector_policy import load_connector_review

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text,
)


runner = CliRunner()


def test_connector_draft_writes_local_review_json(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(),
    )
    output_path = tmp_path / "review.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    review = load_connector_review(output_path)
    assert result.exit_code == 0
    assert "Wrote connector review draft" in result.output
    assert output_path.exists()
    assert review.resource_name == "poe.ninja POE2 Currency"
    assert review.access_method == "api"
    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert review.dry_run_supported is True
    assert review.public_export_derived_only is True
