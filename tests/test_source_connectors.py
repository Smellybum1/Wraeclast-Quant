from pathlib import Path

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources
from connector_policy_helpers import poe_ninja_currency_resource as _poe_ninja_currency_resource
from source_connector_helpers import official_currency_exchange_resource as _official_currency_exchange_resource


def test_fixture_source_connector_returns_normalized_rows() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    connector = FixtureSourceConnector.from_review(
        review,
        _example_approved_api_resources(),
    )

    result = connector.collect_fixture("examples/connector_fixture_api_example.json")

    assert result.connector_id == "fixture-source-connector"
    assert result.connector_class == "FixtureSourceConnector"
    assert result.resource_name == "Example Approved API"
    assert len(result.rows) == 2
    assert result.rows[0].name == "Stormglass Catalyst"


def test_poe_ninja_currency_connector_returns_fixture_rows_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    review_path = Path("examples/reviews/poe_ninja_poe2_currency_connector_review.json").resolve()
    fixture_path = Path("examples/poe_ninja_poe2_currency_fixture.json").resolve()
    review = load_connector_review(review_path)
    monkeypatch.chdir(tmp_path)

    connector = PoeNinjaCurrencyConnector.from_review(
        review,
        [_poe_ninja_currency_resource()],
    )
    result = connector.collect_fixture(fixture_path)

    assert result.connector_id == "poe-ninja-poe2-currency"
    assert result.connector_class == "PoeNinjaCurrencyConnector"
    assert result.resource_name == "poe.ninja POE2 Currency"
    assert [row.name for row in result.rows] == ["Exalted Orb", "Divine Orb", "Chaos Orb"]
    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert not Path("data/raw/cache").exists()


def test_official_currency_exchange_connector_returns_raw_fixture_rows_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    review = load_connector_review("examples/reviews/pathofexile_currency_exchange_connector_review.json")
    fixture_path = Path("examples/pathofexile_currency_exchange_fixture.json").resolve()
    resource = _official_currency_exchange_resource()
    monkeypatch.chdir(tmp_path)

    connector = OfficialCurrencyExchangeConnector.from_review(
        review,
        [resource],
    )
    result = connector.collect_fixture(fixture_path)

    assert result.connector_id == "official-currency-exchange-api"
    assert result.connector_class == "OfficialCurrencyExchangeConnector"
    assert result.resource_name == "Path of Exile Currency Exchange API"
    assert [row.name for row in result.rows] == [
        "Chaos Orb / Divine Orb",
        "Exalted Orb / Divine Orb",
    ]
    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert all(row.signals is None for row in result.rows)
    assert not Path("data/raw/cache").exists()
