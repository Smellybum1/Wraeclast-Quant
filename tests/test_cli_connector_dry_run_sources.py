from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import connector_dry_run_args as _connector_dry_run_args


runner = CliRunner()


def test_connector_dry_run_prints_poe_ninja_currency_connector() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            fixture_path="examples/poe_ninja_poe2_currency_fixture.json",
        ),
    )

    assert result.exit_code == 0
    assert "PoeNinjaCurrencyConnector" in result.output
    assert "poe-ninja-poe2-currency" in result.output
    assert "Exalted Orb" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_prints_official_currency_exchange_connector() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/reviews/pathofexile_currency_exchange_connector_review.json",
            fixture_path="examples/pathofexile_currency_exchange_fixture.json",
        ),
    )

    assert result.exit_code == 0
    assert "OfficialCurrencyExchangeConnector" in result.output
    assert "official-currency-exchange-api" in result.output
    assert "Chaos Orb / Divine Orb" in result.output
    assert "No network requests were made" in result.output
