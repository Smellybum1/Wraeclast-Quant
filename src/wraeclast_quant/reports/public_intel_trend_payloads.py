from __future__ import annotations

from typing import Any

from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def score_trends_payload(
    repository: SnapshotRepository,
    recent_runs: list[AnalysisRunRecord],
    latest_opportunities: list[StoredOpportunityRecord],
) -> list[dict[str, Any]]:
    opportunities_by_run = {
        run.id: {
            opportunity.item_name: opportunity
            for opportunity in repository.scored_opportunities_for_run(run.id)
        }
        for run in recent_runs
    }
    trends = []
    for latest_opportunity in latest_opportunities:
        points = []
        for run in recent_runs:
            opportunity = opportunities_by_run[run.id].get(latest_opportunity.item_name)
            if opportunity is None:
                continue
            points.append(
                {
                    "run_id": run.id,
                    "score": opportunity.opportunity_score,
                    "action": opportunity.action,
                }
            )
        trends.append({"item_name": latest_opportunity.item_name, "points": points})
    return trends
