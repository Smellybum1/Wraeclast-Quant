from typer.testing import CliRunner

from wraeclast_quant.cli import app


runner = CliRunner()


def test_connector_review_status_escapes_endpoint_brackets() -> None:
    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            "examples/reviews/pathofexile_currency_exchange_connector_review.json",
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Status" in result.output
    assert "Path of Exile Currency Exchange API" in result.output
    assert "Authentication approved" in result.output
    assert "Credential storage reviewed" in result.output
