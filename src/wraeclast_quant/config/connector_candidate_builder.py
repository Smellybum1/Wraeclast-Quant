from __future__ import annotations

from wraeclast_quant.config.connector_candidate_commands import (
    draft_command,
    suggested_access_method,
)
from wraeclast_quant.config.connector_candidate_models import ConnectorCandidate
from wraeclast_quant.config.preflight import PreflightAssessment


def candidate_from_assessment(assessment: PreflightAssessment) -> ConnectorCandidate:
    resource = assessment.resource
    is_discord = resource.type.strip().lower() == "discord"
    access_method = suggested_access_method(resource)
    resource_ref = resource.id.strip() if resource.id.strip() else resource.name
    command = ""
    recommendation = "Review source terms before drafting."
    rank = 30

    if assessment.status == "needs-review":
        rank = 0
        recommendation = "Good review candidate; clarify allowed use first."
        command = draft_command(resource_ref, access_method)
    elif assessment.automation_eligible:
        rank = 5
        recommendation = "Eligible for connector review."
        command = draft_command(resource_ref, access_method)
    elif assessment.status == "manual-review":
        rank = 20
        recommendation = "Manual-review only unless source terms change."
        command = draft_command(resource_ref, "manual-export")
        access_method = "manual-export"
    elif is_discord or assessment.status == "discord-gated":
        rank = 90
        recommendation = "Discord-gated; approved-bot/API review required."
        access_method = "manual-export"
    elif assessment.status == "blocked":
        rank = 95
        recommendation = "Blocked; do not automate."
        access_method = "manual-export"

    if is_discord:
        rank = 90
        recommendation = "Discord-gated; approved-bot/API review required."
        command = ""
        access_method = "manual-export"

    return ConnectorCandidate(
        resource=resource,
        preflight=assessment,
        suggested_access_method=access_method,
        draft_command=command,
        recommendation=recommendation,
        rank=rank,
    )


__all__ = ["candidate_from_assessment"]
