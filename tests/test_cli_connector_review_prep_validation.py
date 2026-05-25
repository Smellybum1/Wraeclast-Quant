from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text,
)


runner = CliRunner()


def test_connector_review_prep_untouched_draft_fails_connector_check(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )
    output_dir = tmp_path / "reviews"

    prep_result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(output_dir / "poe_ninja_poe2_currency_connector_review.json"),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert prep_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output
