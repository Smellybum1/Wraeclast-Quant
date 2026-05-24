from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.config.compliance import ComplianceAssessment, assess_resources
from wraeclast_quant.config.resources_loader import Resource, load_resources


@dataclass(frozen=True)
class ResourceStatusContext:
    resources: list[Resource]
    assessments: list[ComplianceAssessment]
    eligible_count: int


def load_resource_status_context(resources_path: Path) -> ResourceStatusContext:
    resources = load_resources(resources_path)
    assessments = assess_resources(resources)
    eligible_count = sum(1 for assessment in assessments if assessment.automation_eligible)
    return ResourceStatusContext(
        resources=resources,
        assessments=assessments,
        eligible_count=eligible_count,
    )


__all__ = ["ResourceStatusContext", "load_resource_status_context"]
