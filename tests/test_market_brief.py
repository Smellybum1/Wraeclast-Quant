from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.reports.market_brief import (
    render_market_brief,
)

from market_brief_helpers import scored_opportunity as _opportunity
from market_brief_helpers import stored_opportunity as _stored


def test_report_renders_without_comparison() -> None:
    report = render_market_brief([_opportunity("Stormglass Catalyst", 70.4, "WATCH")])

    assert "Wraeclast Quant Market Brief" in report
    assert "Snapshot Changes" not in report


def test_report_includes_top_movers() -> None:
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY")],
        latest=[_stored("Stormglass Catalyst", 76.0, "BUY")],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 76.0, "BUY")],
        comparison=comparison,
    )

    assert "## Snapshot Changes" in report
    assert "### Top Score Movers" in report
    assert "| Stormglass Catalyst | 50.00 | 76.00 | +26.00 | BUY |" in report


def test_report_includes_action_new_and_removed_changes() -> None:
    comparison = compare_opportunities(
        previous=[
            _stored("Removed Relic", 42.0, "HOLD / SELL SELECTIVELY"),
            _stored("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY"),
        ],
        latest=[
            _stored("New Catalyst", 60.0, "WATCH"),
            _stored("Stormglass Catalyst", 76.0, "BUY"),
        ],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 76.0, "BUY")],
        comparison=comparison,
    )

    assert "### Action Changes / New / Removed" in report
    assert "| New Catalyst | new |  | WATCH |  |" in report
    assert "| Removed Relic | removed | HOLD / SELL SELECTIVELY |  |  |" in report
    assert "| Stormglass Catalyst | changed | HOLD / SELL SELECTIVELY | BUY | +26.00 |" in report


def test_report_includes_stable_message_when_no_changes() -> None:
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", 70.4, "WATCH")],
        latest=[_stored("Stormglass Catalyst", 70.4, "WATCH")],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 70.4, "WATCH")],
        comparison=comparison,
    )

    assert "## Snapshot Changes" in report
    assert "No score, action, new, or removed item changes were detected." in report
