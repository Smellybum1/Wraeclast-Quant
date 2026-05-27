from wraeclast_quant.reports.static_site import (
    render_static_site,
)

from static_site_helpers import payload as _payload


def test_static_site_renders_title_timestamp_and_run_metadata() -> None:
    html = render_static_site(_payload())

    assert "<h1>Wraeclast Quant</h1>" in html
    assert '<meta name="wq:schema-version" content="1.0">' in html
    assert '<meta name="wq:generated-at" content="2026-05-23T00:00:00+00:00">' in html
    assert '<meta name="wq:latest-run-id" content="7">' in html
    assert '<meta name="wq:latest-run-source-mode" content="sample-data">' in html
    assert '<meta name="wq:latest-run-item-count" content="2">' in html
    assert "<th>Schema version</th><td>1.0</td>" in html
    assert "2026-05-23T00:00:00+00:00" in html
    assert "<th>Latest run</th><td>7</td>" in html
    assert "<th>Source mode</th><td>sample-data</td>" in html
    assert "<th>Item count</th><td>2</td>" in html


def test_static_site_renders_compliance_summary_and_opportunities() -> None:
    html = render_static_site(_payload())

    assert "Compliance Summary" in html
    assert "<th>Total resources</th><td>3</td>" in html
    assert "<th>approved-api</th><td>1</td>" in html
    assert "Stormglass Catalyst" in html
    assert "76.00" in html


def test_static_site_renders_mvp_readiness() -> None:
    html = render_static_site(_payload())

    assert "MVP Readiness" in html
    assert "<th>Local loop</th><td>No-OAuth local decision-support ready</td>" in html
    assert "<th>Latest run</th><td>7</td>" in html
    assert "<th>Review state</th><td>1/2 reviewed</td>" in html
    assert "wq review-queue --run-id 7" in html
    assert "data/processed/review_queue.md" in html
    assert "wq record-outcome --run-id 7" in html


def test_static_site_renders_alerts_and_snapshot_changes() -> None:
    html = render_static_site(_payload())

    assert "Alert Candidates" in html
    assert "Score crossed into BUY" in html
    assert "Snapshot Top Movers" in html
    assert "+26.00" in html
    assert "Action Changes / New / Removed" in html
    assert "changed" in html


def test_static_site_renders_outcome_summary() -> None:
    html = render_static_site(_payload())

    assert "Recommendation Outcome Summary" in html
    assert "<th>positive</th><td>2</td>" in html
    assert "<th>neutral</th><td>1</td>" in html
    assert "<th>negative</th><td>0</td>" in html


def test_static_site_renders_review_coverage() -> None:
    html = render_static_site(_payload())

    assert "Recommendation Review Coverage" in html
    assert "<th>Run</th><td>7</td>" in html
    assert "<th>Total recommendations</th><td>2</td>" in html
    assert "<th>Reviewed</th><td>1</td>" in html
    assert "<th>Unreviewed</th><td>1</td>" in html
    assert "<th>Reviewed %</th><td>50.0%</td>" in html
    assert "<th>Next review action</th>" in html
    assert "wq review-queue --run-id 7" in html
    assert "wq record-outcome --run-id 7" in html
