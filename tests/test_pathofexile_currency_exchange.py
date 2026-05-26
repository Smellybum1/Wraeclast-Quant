from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeMarket,
    currency_exchange_market_item,
    load_currency_exchange_connector_fixture,
    load_currency_exchange_payload,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def test_currency_exchange_fixture_loads_documented_payload_shape() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")

    assert payload.next_change_id == 1770000000
    assert [market.market_id for market in payload.markets] == [
        "chaos|divine",
        "exalted|divine",
    ]
    assert payload.markets[0].volume_traded["chaos"] == 98200


def test_currency_exchange_fixture_converts_to_connector_rows() -> None:
    fixture = load_currency_exchange_connector_fixture(
        "examples/pathofexile_currency_exchange_fixture.json"
    )

    assert fixture.source_name == "Path of Exile Currency Exchange API"
    assert fixture.generated_at == "2026-02-02T02:40:00+00:00"
    assert [item.name for item in fixture.items] == [
        "Chaos Orb / Divine Orb",
        "Exalted Orb / Divine Orb",
    ]
    assert fixture.items[0].category == "currency"
    assert fixture.items[0].signals is None
    assert "hourly aggregate chaos|divine" in fixture.items[0].price_text
    assert "volume chaos=98200, divine=812" in fixture.items[0].notes


def test_currency_exchange_market_id_requires_pipe_pair() -> None:
    market = CurrencyExchangeMarket(
        league="Dawn of the Hunt",
        market_id="chaos-divine",
        volume_traded={"chaos": 1},
        lowest_stock={"chaos": 1},
        highest_stock={"chaos": 1},
        lowest_ratio={"chaos": 1},
        highest_ratio={"chaos": 1},
    )

    with pytest.raises(ConnectorPolicyError, match="market_id"):
        currency_exchange_market_item(1770000000, market)


def test_currency_exchange_invalid_fixture_fails_clearly(tmp_path: Path) -> None:
    fixture_path = tmp_path / "currency_exchange.json"
    fixture_path.write_text('{"markets": []}', encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="Invalid Currency Exchange fixture"):
        load_currency_exchange_payload(fixture_path)
