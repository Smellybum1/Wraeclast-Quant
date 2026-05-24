from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LatestRunSummary:
    id: int
    created_at: str
    source_mode: str
    item_count: int


@dataclass(frozen=True)
class DatabaseContentSummary:
    analysis_run_count: int
    scored_opportunity_count: int
    report_artifact_count: int
    recommendation_outcome_count: int
    latest_run: LatestRunSummary | None


__all__ = ["DatabaseContentSummary", "LatestRunSummary"]
