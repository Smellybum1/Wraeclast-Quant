from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_diagnostics import (
    preview_currency_exchange_baseline_diagnostic,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)


def test_preview_currency_exchange_baseline_diagnostic_applies_freshness_warning() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    current = currency_exchange_market_observation(
        baseline.next_change_id + 10800,
        baseline.markets[0],
    )
    market_history = [
        currency_exchange_market_observation(baseline.next_change_id, baseline.markets[0])
    ]

    diagnostic = preview_currency_exchange_baseline_diagnostic(
        current,
        market_history,
        current_change_id=baseline.next_change_id + 10800,
        expected_cadence_seconds=3600,
        fresh_tolerance_intervals=2,
    )

    assert diagnostic.demand_index == 50.0
    assert diagnostic.liquidity_index == 50.0
    assert diagnostic.spread_index == 50.0
    assert diagnostic.freshness_lag_seconds == 10800
    assert diagnostic.freshness_status == "stale"
    assert diagnostic.stale_data_penalty == 20.0
    assert diagnostic.confidence == "warning"
    assert diagnostic.blockers == ("current payload is stale versus local baseline cadence",)
