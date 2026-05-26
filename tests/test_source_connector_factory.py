from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.source_connector import (
    FixtureSourceConnector,
    source_connector_from_review,
)
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import poe_ninja_currency_resource as _poe_ninja_currency_resource
from source_connector_helpers import official_currency_exchange_resource as _official_currency_exchange_resource


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
