from __future__ import annotations

from pathlib import Path

from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.workflows.daily_pipeline_alerts import create_alert_settings
from wraeclast_quant.workflows.daily_pipeline_artifacts import write_daily_artifacts
from wraeclast_quant.workflows.daily_pipeline_models import DailyPipelineResult, RunProvenanceInput
from wraeclast_quant.workflows.daily_pipeline_provenance import save_run_provenance
from wraeclast_quant.workflows.daily_pipeline_snapshots import create_analysis_snapshot


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
    save_run_provenance(repository, run.id, provenance)
    artifacts = write_daily_artifacts(
        repository=repository,
        run=run,
        opportunities=opportunities,
        resources_path=resources_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        limit=limit,
        alert_settings=alert_settings,
        comparison=comparison,
    )
    if artifacts is None:
        return None

    return DailyPipelineResult(
        repository=repository,
        run=run,
        comparison=comparison,
        alert_candidates=artifacts.alert_candidates,
        brief_path=artifacts.brief_path,
        intel_path=artifacts.intel_path,
        site_path=artifacts.site_path,
    )


__all__ = [
    "DailyPipelineResult",
    "RunProvenanceInput",
    "create_alert_settings",
    "create_analysis_snapshot",
    "run_daily_pipeline",
]
