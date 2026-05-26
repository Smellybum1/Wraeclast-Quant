from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeMarket,
    currency_exchange_market_item,
    currency_exchange_payload_from_manual_snapshot,
    load_currency_exchange_connector_fixture,
    load_currency_exchange_manual_snapshot,
    load_currency_exchange_payload,
    preview_currency_exchange_rolling_baseline_diagnostics,
    preview_currency_exchange_storage_plan,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def test_currency_exchange_manual_snapshot_template_converts_to_payload() -> None:
    payload = load_currency_exchange_manual_snapshot(
        "examples/pathofexile_currency_exchange_manual_snapshot_template.json"
    )

    assert payload.next_change_id == 1770000000
    assert [market.market_id for market in payload.markets] == [
        "chaos|divine",
        "exalted|divine",
    ]
    assert payload.markets[0].volume_traded == {"chaos": 98200, "divine": 812}
    assert payload.markets[0].highest_ratio == {"chaos": 124, "divine": 1}


def test_currency_exchange_manual_snapshot_can_feed_preview_diagnostics() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    payload = load_currency_exchange_manual_snapshot(
        "examples/pathofexile_currency_exchange_manual_snapshot_template.json"
    )

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(payload, [baseline])

    assert diagnostics["chaos|divine"].confidence == "preview"
    assert diagnostics["chaos|divine"].observations == 1
    assert diagnostics["exalted|divine"].confidence == "preview"


def test_currency_exchange_manual_snapshot_rejects_invalid_shape(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "manual_snapshot.json"
    snapshot_path.write_text('{"markets": []}', encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="manual snapshot"):
        load_currency_exchange_manual_snapshot(snapshot_path)


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


def test_currency_exchange_preview_storage_plan_is_non_writing_and_secret_free() -> None:
    plan = preview_currency_exchange_storage_plan()

    assert plan.resource_id == "official_currency_exchange_api"
    assert str(plan.raw_cache_path).replace("\\", "/").endswith(
        "data/raw/cache/path-of-exile-currency-exchange-api-d9b59150fbb2.cache"
    )
    assert str(plan.baseline_observations_path).replace("\\", "/").endswith(
        "data/processed/currency_exchange/baseline_observations.preview.json"
    )
    assert plan.cache_ttl_seconds == 3600
    assert plan.stores_credentials is False
    assert plan.writes_enabled is False


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
