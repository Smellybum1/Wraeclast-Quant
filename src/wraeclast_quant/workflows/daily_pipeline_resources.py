from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.config.compliance import ComplianceAssessment, assess_resources
from wraeclast_quant.config.resources_loader import Resource, load_resources


@dataclass(frozen=True)
class DailyResourceContext:
    resources: list[Resource]
    assessments: list[ComplianceAssessment]


def load_daily_resource_context(resources_path: Path) -> DailyResourceContext:
    resources = load_resources(resources_path)
    return DailyResourceContext(
        resources=resources,
        assessments=assess_resources(resources),
    )


__all__ = ["DailyResourceContext", "load_daily_resource_context"]
