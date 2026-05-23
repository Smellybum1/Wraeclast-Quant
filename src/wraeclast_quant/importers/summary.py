from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.importers.manual import SIGNAL_FIELDS
from wraeclast_quant.intelligence.scoring import ScoredOpportunity


class ManualImportSummary(BaseModel):
    item_count: int
    action_counts: dict[str, int]
    min_score: float
    max_score: float
    average_score: float
    signal_averages: dict[str, float]


def summarize_opportunities(opportunities: list[ScoredOpportunity]) -> ManualImportSummary:
    if not opportunities:
        return ManualImportSummary(
            item_count=0,
            action_counts={},
            min_score=0.0,
            max_score=0.0,
            average_score=0.0,
            signal_averages={field: 0.0 for field in SIGNAL_FIELDS},
        )

    scores = [opportunity.opportunity_score for opportunity in opportunities]
    action_counts: dict[str, int] = {}
    for opportunity in opportunities:
        action_counts[opportunity.action] = action_counts.get(opportunity.action, 0) + 1

    signal_averages = {
        field: round(
            sum(float(getattr(opportunity.inputs, field)) for opportunity in opportunities)
            / len(opportunities),
            2,
        )
        for field in SIGNAL_FIELDS
    }

    return ManualImportSummary(
        item_count=len(opportunities),
        action_counts=dict(sorted(action_counts.items())),
        min_score=round(min(scores), 2),
        max_score=round(max(scores), 2),
        average_score=round(sum(scores) / len(scores), 2),
        signal_averages=signal_averages,
    )
