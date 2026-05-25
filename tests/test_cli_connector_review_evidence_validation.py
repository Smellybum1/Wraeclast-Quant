from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_review_evidence_invalid_values_exit_nonzero(tmp_path: Path) -> None:
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--rate-limit-per-minute",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "rate_limit_per_minute must be positive" in result.output
