from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.intelligence.alerts import AlertCandidate
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
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
