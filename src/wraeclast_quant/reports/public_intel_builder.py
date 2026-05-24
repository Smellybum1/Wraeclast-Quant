from __future__ import annotations

from typing import Any

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel_build_context import load_public_intel_build_context
from wraeclast_quant.reports.public_intel_document import build_public_intel_document
from wraeclast_quant.storage.repositories import SnapshotRepository


def build_public_intel(
    repository: SnapshotRepository,
    resources: list[Resource],
    assessments: list[ComplianceAssessment],
    limit: int = 10,
    generated_at: str | None = None,
    alert_settings: AlertRuleSettings | None = None,
) -> dict[str, Any] | None:
    context = load_public_intel_build_context(
        repository,
        limit=limit,
        alert_settings=alert_settings,
    )
    if context is None:
        return None

    return build_public_intel_document(
        repository=repository,
        context=context,
        resources=resources,
        assessments=assessments,
        limit=limit,
        generated_at=generated_at,
    )
