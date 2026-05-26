from wraeclast_quant.reports.static_site import render_static_site

from static_site_helpers import payload as _payload


def test_static_site_renders_recent_runs_and_score_trends() -> None:
    html = render_static_site(_payload())

    assert "Recent Runs" in html
    assert "<td>7</td><td>2026-05-23T00:00:00+00:00</td><td>sample-data</td><td>2</td>" in html
    assert "Score Trends" in html
    assert "Run #7: 76.00 BUY" in html
    assert "Run #6: 50.00 HOLD / SELL SELECTIVELY" in html
