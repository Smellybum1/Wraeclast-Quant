from __future__ import annotations


def public_intel_payload(run_id: int = 7) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": run_id,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        "recent_runs": [
            {
                "id": run_id,
                "created_at": "2026-05-23T00:00:00+00:00",
                "source_mode": "sample-data",
                "item_count": 1,
            }
        ],
        "top_opportunities": [
            {
                "item_name": "Stormglass Catalyst",
                "opportunity_score": 70.4,
                "action": "WATCH",
            }
        ],
        "score_trends": [
            {
                "item_name": "Stormglass Catalyst",
                "points": [{"run_id": run_id, "score": 70.4, "action": "WATCH"}],
            }
        ],
        "snapshot_changes": {
            "previous_run_id": None,
            "latest_run_id": run_id,
            "top_movers": [],
            "status_changes": [],
        },
        "alerts": [],
        "outcome_summary": {"positive": 0, "neutral": 0, "negative": 0},
        "review_coverage": {
            "run_id": run_id,
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


__all__ = ["public_intel_payload"]
