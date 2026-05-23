import json
from pathlib import Path

from wraeclast_quant.reports.static_site import (
    check_static_site_health,
    load_public_intel,
    render_static_site,
    write_static_site,
)


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


def test_write_static_site_and_load_public_intel(tmp_path: Path) -> None:
    output_path = write_static_site(_payload(), tmp_path / "site")
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_payload()), encoding="utf-8")

    assert output_path == tmp_path / "site" / "index.html"
    assert output_path.exists()
    assert load_public_intel(intel_path)["latest_run"]["id"] == 7
    assert load_public_intel(tmp_path / "missing.json") is None


def test_check_static_site_health_reports_metadata(tmp_path: Path) -> None:
    output_path = write_static_site(_payload(), tmp_path / "site")

    health = check_static_site_health(output_path)

    assert health is not None
    assert health.valid is True
    assert health.missing_markers == []
    assert health.schema_version == "1.0"
    assert health.latest_run_id == 7
    assert health.size_bytes > 0


def test_check_static_site_health_reports_missing_markers(tmp_path: Path) -> None:
    index_path = tmp_path / "site" / "index.html"
    index_path.parent.mkdir()
    index_path.write_text("<html><title>Other</title></html>", encoding="utf-8")

    health = check_static_site_health(index_path)

    assert health is not None
    assert health.valid is False
    assert "heading" in health.missing_markers
    assert "schema-version" in health.missing_markers
    assert health.schema_version == ""
    assert health.latest_run_id is None


def test_check_static_site_health_missing_file_returns_none(tmp_path: Path) -> None:
    assert check_static_site_health(tmp_path / "missing" / "index.html") is None


def _payload():
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": 7,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 2,
        },
        "compliance_summary": {
            "total_resources": 3,
            "automation_eligible_count": 1,
            "status_counts": {
                "approved-api": 1,
                "manual-review": 1,
                "needs-review": 1,
            },
        },
        "outcome_summary": {
            "positive": 2,
            "neutral": 1,
            "negative": 0,
        },
        "review_coverage": {
            "run_id": 7,
            "total_recommendations": 2,
            "reviewed_recommendations": 1,
            "unreviewed_recommendations": 1,
            "reviewed_percent": 50.0,
        },
        "alerts": [
            {
                "severity": "high",
                "item_name": "Stormglass Catalyst",
                "reason": "Score crossed into BUY",
                "latest_score": 76.0,
                "score_delta": 26.0,
            }
        ],
        "top_opportunities": [
            {
                "item_name": "Stormglass Catalyst",
                "opportunity_score": 76.0,
                "action": "BUY",
            }
        ],
        "recent_runs": [
            {
                "id": 7,
                "created_at": "2026-05-23T00:00:00+00:00",
                "source_mode": "sample-data",
                "item_count": 2,
            },
            {
                "id": 6,
                "created_at": "2026-05-22T00:00:00+00:00",
                "source_mode": "manual-import",
                "item_count": 2,
            },
        ],
        "score_trends": [
            {
                "item_name": "Stormglass Catalyst",
                "points": [
                    {"run_id": 7, "score": 76.0, "action": "BUY"},
                    {
                        "run_id": 6,
                        "score": 50.0,
                        "action": "HOLD / SELL SELECTIVELY",
                    },
                ],
            }
        ],
        "snapshot_changes": {
            "previous_run_id": 6,
            "latest_run_id": 7,
            "top_movers": [
                {
                    "item_name": "Stormglass Catalyst",
                    "previous_score": 50.0,
                    "latest_score": 76.0,
                    "score_delta": 26.0,
                    "latest_action": "BUY",
                }
            ],
            "status_changes": [
                {
                    "item_name": "Stormglass Catalyst",
                    "status": "changed",
                    "previous_action": "HOLD / SELL SELECTIVELY",
                    "latest_action": "BUY",
                    "score_delta": 26.0,
                }
            ],
        },
    }
