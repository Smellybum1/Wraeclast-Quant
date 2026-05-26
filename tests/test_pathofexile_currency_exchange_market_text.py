import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange_market_text import (
    currency_exchange_currency_label,
    currency_exchange_market_pair,
    format_currency_exchange_mapping,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def test_currency_exchange_market_pair_parses_pipe_separated_codes() -> None:
    assert currency_exchange_market_pair("chaos | divine") == ("chaos", "divine")


def test_currency_exchange_market_pair_rejects_invalid_shape() -> None:
    with pytest.raises(ConnectorPolicyError, match="market_id"):
        currency_exchange_market_pair("chaos-divine")


def test_currency_exchange_currency_label_formats_known_and_unknown_codes() -> None:
    assert currency_exchange_currency_label("chaos") == "Chaos Orb"
    assert currency_exchange_currency_label("lesser_jewellers_orb") == "Lesser Jewellers Orb"


def test_format_currency_exchange_mapping_sorts_keys() -> None:
    assert format_currency_exchange_mapping({"divine": 2, "chaos": 100}) == "chaos=100, divine=2"
