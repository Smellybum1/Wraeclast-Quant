from wraeclast_quant.reports.static_site import render_static_site

from static_site_helpers import payload as _payload


def test_static_site_renders_empty_states() -> None:
    payload = _payload()
    payload["alerts"] = []
    payload["snapshot_changes"]["top_movers"] = []
    payload["snapshot_changes"]["status_changes"] = []
    payload["recent_runs"] = []
    payload["score_trends"] = []
    payload["review_coverage"] = {}
    payload["outcome_summary"] = {}

    html = render_static_site(payload)

    assert "No alert candidates." in html
    assert "No score changes." in html
    assert "No action, new, or removed changes." in html
    assert "No recent runs." in html
    assert "No score trends." in html
    assert "<th>Reviewed %</th><td>0.0%</td>" in html
    assert "<th>positive</th><td>0</td>" in html


def test_static_site_escapes_html() -> None:
    payload = _payload()
    payload["top_opportunities"][0]["item_name"] = "<script>alert('x')</script>"
    payload["alerts"][0]["reason"] = "<b>bad</b>"
    payload["score_trends"][0]["item_name"] = "<img src=x onerror=alert(1)>"
    payload["latest_run"]["source_mode"] = '"manual" <bad>'

    html = render_static_site(payload)

    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html
    assert "<b>bad</b>" not in html
    assert "&lt;b&gt;bad&lt;/b&gt;" in html
    assert "<img src=x" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert 'content="&quot;manual&quot; &lt;bad&gt;"' in html
