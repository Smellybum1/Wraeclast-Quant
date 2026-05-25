import json
from pathlib import Path


def write_public_intel_payload(tmp_path: Path, payload: dict[str, object]) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    return intel_path


def public_intel_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": 7,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        "recent_runs": [
            {
                "id": 7,
                "created_at": "2026-05-23T00:00:00+00:00",
                "source_mode": "sample-data",
                "item_count": 1,
            }
        ],
        "top_opportunities": [
            {
                "item_name": "Stormglass Catalyst",
                "opportunity_score": 76.0,
                "action": "BUY",
            }
        ],
        "score_trends": [
            {
                "item_name": "Stormglass Catalyst",
                "points": [{"run_id": 7, "score": 76.0, "action": "BUY"}],
            }
        ],
        "snapshot_changes": {
            "previous_run_id": None,
            "latest_run_id": 7,
            "top_movers": [],
            "status_changes": [],
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
        "outcome_summary": {"positive": 0, "neutral": 0, "negative": 0},
        "review_coverage": {
            "run_id": 7,
            "total_recommendations": 1,
            "reviewed_recommendations": 0,
            "unreviewed_recommendations": 1,
            "reviewed_percent": 0.0,
        },
        "compliance_summary": {
            "total_resources": 1,
            "status_counts": {"manual-review": 1},
            "automation_eligible_count": 0,
        },
    }
