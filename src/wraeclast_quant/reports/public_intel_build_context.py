from __future__ import annotations

from dataclasses import dataclass

from wraeclast_quant.intelligence.alerts import AlertCandidate, AlertRuleSettings, generate_alerts
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.reports.public_intel_snapshot_context import build_snapshot_comparison
from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


@dataclass(frozen=True)
class PublicIntelBuildContext:
    latest: AnalysisRunRecord
    latest_opportunities: list[StoredOpportunityRecord]
    recent_runs: list[AnalysisRunRecord]
    comparison: SnapshotComparison | None
    alerts: list[AlertCandidate]


def load_public_intel_build_context(
    repository: SnapshotRepository,
    *,
    limit: int,
    alert_settings: AlertRuleSettings | None = None,
) -> PublicIntelBuildContext | None:
    latest = repository.latest_run()
    if latest is None:
        return None

    latest_opportunities = repository.scored_opportunities_for_run(latest.id, limit=limit)
    recent_runs = repository.list_recent_runs(limit=limit)
    previous = repository.previous_run_before(latest.id)
    comparison = build_snapshot_comparison(repository, previous, latest)
    alerts = generate_alerts(comparison, settings=alert_settings) if comparison is not None else []
    return PublicIntelBuildContext(
        latest=latest,
        latest_opportunities=latest_opportunities,
        recent_runs=recent_runs,
        comparison=comparison,
        alerts=alerts,
    )
