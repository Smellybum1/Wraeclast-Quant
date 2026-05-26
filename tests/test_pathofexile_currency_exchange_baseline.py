from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
    preview_currency_exchange_opportunity_inputs,
    preview_currency_exchange_rolling_baseline_diagnostics,
)


def test_currency_exchange_rolling_baseline_is_stable_across_payload_composition() -> None:
    history = [load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")]
    narrow = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json"),
        history,
    )
    broad = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json"),
        history,
    )

    assert narrow["chaos|divine"].demand_index == broad["chaos|divine"].demand_index
    assert narrow["chaos|divine"].liquidity_index == broad["chaos|divine"].liquidity_index
    assert narrow["chaos|divine"].spread_index == broad["chaos|divine"].spread_index
    assert broad["chaos|divine"].freshness_lag_seconds == 7200
    assert broad["chaos|divine"].freshness_status == "fresh"
    assert broad["chaos|divine"].stale_data_penalty == 0.0
    assert broad["chaos|regal"].confidence == "blocked"
    assert broad["chaos|regal"].blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_surfaces_thin_market_diagnostics() -> None:
    history = [load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")]
    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_low_liquidity_fixture.json"),
        history,
    )

    thin = diagnostics["chaos|divine"]
    liquid = diagnostics["exalted|divine"]
    assert thin.observations == 1
    assert thin.demand_index == 0.46
    assert thin.liquidity_index == 0.98
    assert thin.spread_index == 100.0
    assert thin.confidence == "preview"
    assert liquid.demand_index == 50.87
    assert liquid.liquidity_index == 51.44
    assert liquid.spread_index == 60.08


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


def test_currency_exchange_rolling_baseline_requires_local_history() -> None:
    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json"),
        [],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.observations == 0
    assert chaos_divine.demand_index == 0.0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_keeps_leagues_separate() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    other_league_current = baseline.model_copy(
        update={
            "markets": [
                market.model_copy(update={"league": "Different League"})
                for market in baseline.markets
            ]
        }
    )

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        other_league_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.league == "Different League"
    assert chaos_divine.observations == 0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_honors_minimum_history() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        baseline,
        [baseline],
        min_observations=2,
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.observations == 1
    assert chaos_divine.demand_index == 0.0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_opportunity_inputs_skip_warning_diagnostics() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    stale_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id + 10800})
    diagnostic = preview_currency_exchange_rolling_baseline_diagnostics(
        stale_current,
        [baseline],
    )["chaos|divine"]

    assert diagnostic.confidence == "warning"
    assert preview_currency_exchange_opportunity_inputs(diagnostic) is None
