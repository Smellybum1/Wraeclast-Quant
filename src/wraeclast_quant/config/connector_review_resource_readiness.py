from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorReview
from wraeclast_quant.config.connector_policy_utils import find_resource
from wraeclast_quant.config.preflight import PreflightAssessment, assess_preflight_resource
from wraeclast_quant.config.resources_loader import Resource


def resource_readiness(
    review: ConnectorReview,
    resources: list[Resource],
    blockers: list[str],
) -> tuple[Resource | None, PreflightAssessment | None]:
    resource = find_resource(review.resource_name, resources)
    preflight = None

    if resource is None:
        blockers.append("No matching resource found in RESOURCES.md.")
    else:
        preflight = assess_preflight_resource(resource)
        if not preflight.automation_eligible:
            blockers.append(
                f"Resource is not automation-eligible: {preflight.status} - {preflight.reason}"
            )
        if resource.type.strip().lower() == "discord":
            blockers.append("Discord resources require explicit approved-bot/API review.")

    return resource, preflight


__all__ = ["resource_readiness"]
