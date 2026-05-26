from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_connector_fixture,
    load_currency_exchange_payload,
    preview_currency_exchange_signal_inputs,
)


def test_currency_exchange_preview_signals_are_deterministic_and_unwired() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    fixture = load_currency_exchange_connector_fixture(
        "examples/pathofexile_currency_exchange_fixture.json"
    )

    signals = preview_currency_exchange_signal_inputs(payload)

    chaos_divine = signals["chaos|divine"]
    exalted_divine = signals["exalted|divine"]
    assert chaos_divine.demand_momentum == 100.0
    assert chaos_divine.liquidity_score == 92.53
    assert chaos_divine.manipulation_risk == 5.64
    assert exalted_divine.demand_momentum == 52.32
    assert exalted_divine.liquidity_score == 66.62
    assert exalted_divine.manipulation_risk == 21.48
    assert chaos_divine.build_dependency_score == 50.0
    assert chaos_divine.price_discount_score == 50.0
    assert chaos_divine.historical_spike_score == 50.0
    assert chaos_divine.patch_relevance_score == 50.0
    assert chaos_divine.stale_data_penalty == 20.0
    assert all(item.signals is None for item in fixture.items)


def test_currency_exchange_preview_signals_handle_empty_payload() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    empty_payload = payload.model_copy(update={"markets": []})

    assert preview_currency_exchange_signal_inputs(empty_payload) == {}
