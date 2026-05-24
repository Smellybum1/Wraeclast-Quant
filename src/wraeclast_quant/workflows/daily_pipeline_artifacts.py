from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.intelligence.alerts import AlertCandidate, AlertRuleSettings, generate_alerts
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.reports.public_intel import build_public_intel, write_public_intel
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository
from wraeclast_quant.workflows.daily_pipeline_resources import load_daily_resource_context


@dataclass(frozen=True)
class DailyArtifactOutput:
    alert_candidates: list[AlertCandidate]
    brief_path: Path
    intel_path: Path
    site_path: Path


def write_daily_artifacts(
    *,
    repository: SnapshotRepository,
    run: AnalysisRunRecord,
    opportunities: list[ScoredOpportunity],
    resources_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    limit: int,
    alert_settings: AlertRuleSettings,
    comparison: SnapshotComparison | None,
) -> DailyArtifactOutput | None:
    resource_context = load_daily_resource_context(resources_path)

    written_brief_path = write_market_brief(
        opportunities,
        path=brief_path,
        comparison=comparison,
    )
    repository.save_report_artifact(run.id, written_brief_path)

    payload = build_public_intel(
        repository=repository,
        resources=resource_context.resources,
        assessments=resource_context.assessments,
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

    return DailyArtifactOutput(
        alert_candidates=alert_candidates,
        brief_path=written_brief_path,
        intel_path=written_intel_path,
        site_path=written_site_path,
    )
