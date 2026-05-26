from wraeclast_quant.collectors.pathofexile_currency_exchange_manual_conversion import (
    currency_exchange_manual_currency_code,
    currency_exchange_market_from_manual_market,
    currency_exchange_payload_from_manual_snapshot,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
)


def _manual_market() -> CurrencyExchangeManualMarket:
    return CurrencyExchangeManualMarket(
        league="Dawn of the Hunt",
        left_currency="Chaos Orb",
        right_currency="Divine Orb",
        left_volume_traded=98200,
        right_volume_traded=812,
        left_lowest_stock=1200,
        right_lowest_stock=16,
        left_highest_stock=2500,
        right_highest_stock=22,
        left_lowest_ratio=121,
        right_lowest_ratio=1,
        left_highest_ratio=124,
        right_highest_ratio=1,
    )


def test_currency_exchange_manual_currency_code_normalizes_display_name() -> None:
    assert currency_exchange_manual_currency_code(" Lesser Jeweller's Orb ") == "lesser_jeweller's_orb"


def test_currency_exchange_market_from_manual_market_preserves_all_numeric_fields() -> None:
    market = currency_exchange_market_from_manual_market(_manual_market())

    assert market.market_id == "chaos_orb|divine_orb"
    assert market.volume_traded == {"chaos_orb": 98200, "divine_orb": 812}
    assert market.lowest_stock == {"chaos_orb": 1200, "divine_orb": 16}
    assert market.highest_stock == {"chaos_orb": 2500, "divine_orb": 22}
    assert market.lowest_ratio == {"chaos_orb": 121, "divine_orb": 1}
    assert market.highest_ratio == {"chaos_orb": 124, "divine_orb": 1}


def test_currency_exchange_payload_from_manual_snapshot_preserves_next_change_id() -> None:
    payload = currency_exchange_payload_from_manual_snapshot(
        CurrencyExchangeManualSnapshot(next_change_id=1770000000, markets=[_manual_market()])
    )

    assert payload.next_change_id == 1770000000
    assert len(payload.markets) == 1
