from __future__ import annotations

from wraeclast_quant.config.compliance_models import ComplianceAssessment
from wraeclast_quant.config.resources_loader import Resource


def assess_resource(resource: Resource) -> ComplianceAssessment:
    allowed_use = resource.allowed_use.strip().lower()
    resource_type = resource.type.strip().lower()

    if allowed_use in {"no-automation", "blocked"}:
        return ComplianceAssessment(
            resource=resource,
            status="blocked",
            automation_eligible=False,
            reason="Source is explicitly marked no-automation or blocked.",
        )

    if resource_type == "discord":
        return ComplianceAssessment(
            resource=resource,
            status="manual-review",
            automation_eligible=False,
            reason="Discord requires explicit approved-bot/API compliance review.",
        )

    if allowed_use == "api":
        return ComplianceAssessment(
            resource=resource,
            status="approved-api",
            automation_eligible=True,
            reason="Resource is explicitly marked for API use.",
        )

    if allowed_use == "rss":
        return ComplianceAssessment(
            resource=resource,
            status="approved-rss",
            automation_eligible=True,
            reason="Resource is explicitly marked for RSS use.",
        )

    if allowed_use == "download":
        return ComplianceAssessment(
            resource=resource,
            status="approved-download",
            automation_eligible=True,
            reason="Resource is explicitly marked for downloadable data use.",
        )

    if allowed_use == "manual-review":
        return ComplianceAssessment(
            resource=resource,
            status="manual-review",
            automation_eligible=False,
            reason="Manual review only.",
        )

    return ComplianceAssessment(
        resource=resource,
        status="needs-review",
        automation_eligible=False,
        reason="Allowed use is conditional or unclear; review source terms before automation.",
    )


def assess_resources(resources: list[Resource]) -> list[ComplianceAssessment]:
    return [assess_resource(resource) for resource in resources]


__all__ = ["ComplianceAssessment", "assess_resource", "assess_resources"]
