from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources
from wraeclast_quant.intelligence.alerts import AlertCandidate, AlertRuleSettings, generate_alerts
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison, compare_opportunities
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.reports.public_intel import build_public_intel, write_public_intel
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


@dataclass(frozen=True)
class RunProvenanceInput:
    source_kind: str
    resource_name: str
    connector_id: str
    access_method: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class DailyPipelineResult:
    repository: SnapshotRepository
    run: AnalysisRunRecord
    comparison: SnapshotComparison | None
    alert_candidates: list[AlertCandidate]
    brief_path: Path
    intel_path: Path
    site_path: Path


def create_alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    return AlertRuleSettings(
        watch_threshold=watch_threshold,
        buy_threshold=buy_threshold,
        big_positive_delta=big_delta,
    )


def run_daily_pipeline(
    *,
    opportunities: list[ScoredOpportunity],
    source_mode: str,
    database_path: Path,
    resources_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    limit: int,
    alert_settings: AlertRuleSettings,
    provenance: RunProvenanceInput | None = None,
) -> DailyPipelineResult | None:
    repository, run, comparison = create_analysis_snapshot(
        database_path,
        opportunities,
        source_mode=source_mode,
    )
    if provenance is not None:
        repository.save_run_provenance(
            run_id=run.id,
            source_kind=provenance.source_kind,
            resource_name=provenance.resource_name,
            connector_id=provenance.connector_id,
            access_method=provenance.access_method,
            metadata=provenance.metadata,
        )

    resources = load_resources(resources_path)
    assessments = assess_resources(resources)

    written_brief_path = write_market_brief(
        opportunities,
        path=brief_path,
        comparison=comparison,
    )
    repository.save_report_artifact(run.id, written_brief_path)

    payload = build_public_intel(
        repository=repository,
        resources=resources,
        assessments=assessments,
        limit=limit,
        alert_settings=alert_settings,
    )
    if payload is None:
        return None

    written_intel_path = write_public_intel(payload, intel_path)
    written_site_path = write_static_site(payload, site_dir)
    alert_candidates = []
    if comparison is not None:
        alert_candidates = generate_alerts(comparison, settings=alert_settings)

    return DailyPipelineResult(
        repository=repository,
        run=run,
        comparison=comparison,
        alert_candidates=alert_candidates,
        brief_path=written_brief_path,
        intel_path=written_intel_path,
        site_path=written_site_path,
    )


def create_analysis_snapshot(
    database_path: Path,
    opportunities: list[ScoredOpportunity],
    source_mode: str,
) -> tuple[SnapshotRepository, AnalysisRunRecord, SnapshotComparison | None]:
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode=source_mode, item_count=len(opportunities))
    previous = repository.previous_run_before(run.id)
    repository.save_scored_opportunities(run.id, opportunities)
    comparison = None
    if previous is not None:
        comparison = compare_opportunities(
            previous=repository.scored_opportunities_for_run(previous.id),
            latest=repository.scored_opportunities_for_run(run.id),
            previous_run_id=previous.id,
            latest_run_id=run.id,
        )
    return repository, run, comparison
