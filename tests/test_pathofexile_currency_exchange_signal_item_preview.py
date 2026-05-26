from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_baseline_diagnostics import (
    preview_currency_exchange_baseline_diagnostic,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import (
    currency_exchange_market_observation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_signal_fixture_preview import (
    preview_currency_exchange_signal_item,
)


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
