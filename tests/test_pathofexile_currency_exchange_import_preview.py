from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_diagnostics import (
    preview_currency_exchange_baseline_diagnostic,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_opportunity_preview import (
    preview_currency_exchange_opportunity_inputs,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_signal_fixture_preview import (
    preview_currency_exchange_signal_item,
)


def test_currency_exchange_opportunity_preview_maps_baseline_diagnostic_to_signals() -> None:
    diagnostic = CurrencyExchangeBaselineDiagnostics(
        league="Dawn of the Hunt",
        market_id="chaos|divine",
        observations=3,
        demand_index=42.0,
        liquidity_index=80.0,
        spread_index=10.0,
        freshness_lag_seconds=3600,
        freshness_status="fresh",
        stale_data_penalty=0.0,
        confidence="preview",
    )

    signals = preview_currency_exchange_opportunity_inputs(diagnostic)

    assert signals is not None
    assert signals.demand_momentum == 42.0
    assert signals.liquidity_score == 80.0
    assert signals.manipulation_risk == 15.0
    assert signals.stale_data_penalty == 0.0


def test_currency_exchange_opportunity_preview_blocks_warning_diagnostic() -> None:
    diagnostic = CurrencyExchangeBaselineDiagnostics(
        league="Dawn of the Hunt",
        market_id="chaos|divine",
        observations=3,
        demand_index=42.0,
        liquidity_index=80.0,
        spread_index=10.0,
        freshness_lag_seconds=10800,
        freshness_status="stale",
        stale_data_penalty=20.0,
        confidence="warning",
        blockers=("current payload is stale versus local baseline cadence",),
    )

    assert preview_currency_exchange_opportunity_inputs(diagnostic) is None


def test_currency_exchange_signal_item_appends_preview_metadata_and_signals() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    current = currency_exchange_market_observation(baseline.next_change_id, baseline.markets[0])
    diagnostic = preview_currency_exchange_baseline_diagnostic(
        current,
        [current],
        current_change_id=baseline.next_change_id,
        expected_cadence_seconds=3600,
        fresh_tolerance_intervals=2,
    )

    item = preview_currency_exchange_signal_item(
        baseline.next_change_id,
        baseline.markets[0],
        diagnostic,
    )

    assert item.name == "Chaos Orb / Divine Orb"
    assert item.confidence == "preview"
    assert item.signals is not None
    assert "preview baseline confidence preview" in item.notes
    assert "observations 1" in item.notes
    assert "freshness fresh" in item.notes
