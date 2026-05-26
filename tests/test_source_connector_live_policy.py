import pytest

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import poe_ninja_currency_resource as _poe_ninja_currency_resource
from source_connector_helpers import official_currency_exchange_resource as _official_currency_exchange_resource


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
