def payload():
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
