from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
    preview_currency_exchange_signal_inputs,
)


def test_currency_exchange_preview_signals_surface_low_liquidity_spread_risk() -> None:
    payload = load_currency_exchange_payload(
        "examples/pathofexile_currency_exchange_low_liquidity_fixture.json"
    )

    signals = preview_currency_exchange_signal_inputs(payload)

    thin = signals["chaos|divine"]
    liquid = signals["exalted|divine"]
    assert thin.demand_momentum == 1.72
    assert thin.liquidity_score == 2.15
    assert thin.manipulation_risk == 70.38
    assert liquid.demand_momentum == 100.0
    assert liquid.liquidity_score == 100.0
    assert liquid.manipulation_risk == 1.74


def test_currency_exchange_preview_signals_show_relative_payload_sensitivity() -> None:
    narrow = preview_currency_exchange_signal_inputs(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    )
    broad = preview_currency_exchange_signal_inputs(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json")
    )

    assert narrow["chaos|divine"].demand_momentum == 100.0
    assert broad["chaos|divine"].demand_momentum == 42.31
    assert narrow["chaos|divine"].liquidity_score == 92.53
    assert broad["chaos|divine"].liquidity_score == 33.75
    assert narrow["exalted|divine"].liquidity_score == 66.62
    assert broad["exalted|divine"].liquidity_score == 21.0
