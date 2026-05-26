from wraeclast_quant.reports.market_brief import (
    render_market_brief,
)

from market_brief_helpers import scored_opportunity as _opportunity


def test_report_renders_without_comparison() -> None:
    report = render_market_brief([_opportunity("Stormglass Catalyst", 70.4, "WATCH")])

    assert "Wraeclast Quant Market Brief" in report
    assert "Snapshot Changes" not in report
