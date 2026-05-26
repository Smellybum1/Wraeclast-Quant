import json
from pathlib import Path

from wraeclast_quant.reports.static_site import (
    load_public_intel,
    render_static_site,
    write_static_site,
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


def test_static_site_renders_alerts_and_snapshot_changes() -> None:
    html = render_static_site(_payload())

    assert "Alert Candidates" in html
    assert "Score crossed into BUY" in html
    assert "Snapshot Top Movers" in html
    assert "+26.00" in html
    assert "Action Changes / New / Removed" in html
    assert "changed" in html


def test_static_site_renders_recent_runs_and_score_trends() -> None:
    html = render_static_site(_payload())

    assert "Recent Runs" in html
    assert "<td>7</td><td>2026-05-23T00:00:00+00:00</td><td>sample-data</td><td>2</td>" in html
    assert "Score Trends" in html
    assert "Run #7: 76.00 BUY" in html
    assert "Run #6: 50.00 HOLD / SELL SELECTIVELY" in html


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
    assert "wq review-queue" in html
    assert "wq record-outcome --run-id 7" in html


def test_write_static_site_and_load_public_intel(tmp_path: Path) -> None:
    output_path = write_static_site(_payload(), tmp_path / "site")
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_payload()), encoding="utf-8")

    assert output_path == tmp_path / "site" / "index.html"
    assert output_path.exists()
    assert load_public_intel(intel_path)["latest_run"]["id"] == 7
    assert load_public_intel(tmp_path / "missing.json") is None
