from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
    preview_currency_exchange_opportunity_inputs,
    preview_currency_exchange_rolling_baseline_diagnostics,
)


def test_currency_exchange_rolling_baseline_flags_stale_cadence() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    stale_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id + 10800})

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        stale_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.freshness_lag_seconds == 10800
    assert chaos_divine.freshness_status == "stale"
    assert chaos_divine.stale_data_penalty == 20.0
    assert chaos_divine.confidence == "warning"
    assert chaos_divine.blockers == ("current payload is stale versus local baseline cadence",)


def test_currency_exchange_rolling_baseline_flags_out_of_order_capture() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    older_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id - 3600})

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        older_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.freshness_lag_seconds == -3600
    assert chaos_divine.freshness_status == "out-of-order"
    assert chaos_divine.stale_data_penalty == 40.0
    assert chaos_divine.confidence == "warning"
    assert chaos_divine.blockers == ("current payload predates local baseline history",)


def test_currency_exchange_opportunity_inputs_skip_warning_diagnostics() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    stale_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id + 10800})
    diagnostic = preview_currency_exchange_rolling_baseline_diagnostics(
        stale_current,
        [baseline],
    )["chaos|divine"]

    assert diagnostic.confidence == "warning"
    assert preview_currency_exchange_opportunity_inputs(diagnostic) is None
