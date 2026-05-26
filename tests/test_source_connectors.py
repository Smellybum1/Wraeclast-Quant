from pathlib import Path

import pytest

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.source_connector import (
    FixtureSourceConnector,
    source_connector_from_review,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.connector_policy import load_connector_review
from wraeclast_quant.config.resources_loader import load_resources

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources
from connector_policy_helpers import minimal_fixture_payload as _minimal_fixture_payload
from connector_policy_helpers import poe_ninja_currency_resource as _poe_ninja_currency_resource
from connector_policy_helpers import write_connector_fixture as _write_connector_fixture


def _official_currency_exchange_resource():
    return [
        resource
        for resource in load_resources("RESOURCES.md")
        if resource.id == "official_currency_exchange_api"
    ][0]


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


def test_source_connector_factory_selects_poe_ninja_currency_connector() -> None:
    review = load_connector_review("examples/reviews/poe_ninja_poe2_currency_connector_review.json")

    connector = source_connector_from_review(review, [_poe_ninja_currency_resource()])

    assert isinstance(connector, PoeNinjaCurrencyConnector)
    assert connector.connector_id == "poe-ninja-poe2-currency"


def test_source_connector_factory_selects_official_currency_exchange_connector() -> None:
    review = load_connector_review("examples/reviews/pathofexile_currency_exchange_connector_review.json")

    connector = source_connector_from_review(review, [_official_currency_exchange_resource()])

    assert isinstance(connector, OfficialCurrencyExchangeConnector)
    assert connector.connector_id == "official-currency-exchange-api"


def test_source_connector_factory_keeps_generic_fixture_connector() -> None:
    connector = source_connector_from_review(_review(), [_eligible_resource()])

    assert isinstance(connector, FixtureSourceConnector)
    assert not isinstance(connector, PoeNinjaCurrencyConnector)
    assert connector.connector_id == "fixture-source-connector"


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


def test_poe_ninja_currency_connector_refuses_other_resources() -> None:
    with pytest.raises(ConnectorPolicyError, match="poe_ninja_poe2_currency"):
        PoeNinjaCurrencyConnector.from_review(_review(), [_eligible_resource()])


def test_official_currency_exchange_connector_refuses_other_resources() -> None:
    with pytest.raises(ConnectorPolicyError, match="official_currency_exchange_api"):
        OfficialCurrencyExchangeConnector.from_review(_review(), [_eligible_resource()])


def test_poe_ninja_currency_connector_live_collection_is_unsupported() -> None:
    review = load_connector_review("examples/reviews/poe_ninja_poe2_currency_connector_review.json")
    connector = PoeNinjaCurrencyConnector.from_review(
        review,
        [_poe_ninja_currency_resource()],
    )

    with pytest.raises(ConnectorPolicyError, match="Live connector collection is unsupported") as exc_info:
        connector.collect_live()

    error = str(exc_info.value)
    assert "poe.ninja POE2 Currency" in error
    assert "machine endpoint URL" in error
    assert "response-field schema" in error
    assert "source-owner reuse" in error


def test_official_currency_exchange_connector_live_collection_is_unsupported() -> None:
    review = load_connector_review("examples/reviews/pathofexile_currency_exchange_connector_review.json")
    connector = OfficialCurrencyExchangeConnector.from_review(
        review,
        [_official_currency_exchange_resource()],
    )

    with pytest.raises(ConnectorPolicyError, match="Live connector collection is unsupported") as exc_info:
        connector.collect_live()

    error = str(exc_info.value)
    assert "Path of Exile Currency Exchange API" in error
    assert "OAuth token exchange" in error
    assert "Credential storage outside the repo" in error
    assert "cache writes" in error


def test_fixture_source_connector_live_collection_is_unsupported() -> None:
    connector = FixtureSourceConnector.from_review(_review(), [_eligible_resource()])

    with pytest.raises(ConnectorPolicyError, match="Live connector collection is unsupported"):
        connector.collect_live()


def test_fixture_source_connector_refuses_incomplete_review() -> None:
    with pytest.raises(ConnectorPolicyError, match="Source terms must be reviewed"):
        FixtureSourceConnector.from_review(
            _review(source_terms_reviewed=False),
            [_eligible_resource()],
        )


def test_fixture_source_connector_exposes_fetch_plan_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_connector_fixture(tmp_path, _minimal_fixture_payload())
    connector = FixtureSourceConnector.from_review(_review(), [_eligible_resource()])
    result = connector.collect_fixture(fixture_path)

    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert not Path("data/raw/cache").exists()
