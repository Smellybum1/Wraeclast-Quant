from __future__ import annotations

import re

from pydantic import BaseModel

from wraeclast_quant.config.preflight import PreflightAssessment, assess_preflight_resources
from wraeclast_quant.config.resources_loader import Resource


class ConnectorCandidate(BaseModel):
    resource: Resource
    preflight: PreflightAssessment
    suggested_access_method: str
    draft_command: str
    recommendation: str
    rank: int


def connector_candidates(resources: list[Resource], limit: int = 10) -> list[ConnectorCandidate]:
    candidates = [_candidate_from_assessment(assessment) for assessment in assess_preflight_resources(resources)]
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            candidate.rank,
            _priority_rank(candidate.resource.priority),
            candidate.resource.name.casefold(),
        ),
    )
    return ranked[:limit]


def suggested_access_method(resource: Resource) -> str:
    allowed_use = resource.allowed_use.strip().lower()
    if "rss" in allowed_use:
        return "rss"
    if "api" in allowed_use:
        return "api"
    if "download" in allowed_use:
        return "download"
    return "manual-export"


def _candidate_from_assessment(assessment: PreflightAssessment) -> ConnectorCandidate:
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
        command = _draft_command(resource_ref, access_method)
    elif assessment.automation_eligible:
        rank = 5
        recommendation = "Eligible for connector review."
        command = _draft_command(resource_ref, access_method)
    elif assessment.status == "manual-review":
        rank = 20
        recommendation = "Manual-review only unless source terms change."
        command = _draft_command(resource_ref, "manual-export")
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


def _draft_command(resource_ref: str, access_method: str) -> str:
    output_name = _safe_slug(resource_ref) + "_connector_review.json"
    parts = [
        "wq",
        "connector-draft",
        "--resource",
        resource_ref,
        "--access-method",
        access_method,
        "--output-path",
        f"examples/{output_name}",
    ]
    return " ".join(_quote_cli_arg(part) for part in parts)


def _priority_rank(priority: str) -> int:
    return {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }.get(priority.strip().lower(), 4)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return slug.strip("_") or "resource"


def _quote_cli_arg(value: str) -> str:
    if not value or any(character.isspace() for character in value) or '"' in value:
        return f'"{value.replace(chr(34), chr(92) + chr(34))}"'
    return value
