from __future__ import annotations

from wraeclast_quant.collectors.registry import collector_for
from wraeclast_quant.config.compliance import assess_resource
from wraeclast_quant.config.preflight_models import PreflightAssessment
from wraeclast_quant.config.preflight_next_steps import fallback_next_step
from wraeclast_quant.config.preflight_special_cases import special_preflight_assessment
from wraeclast_quant.config.resources_loader import Resource


def assess_preflight_resource(resource: Resource) -> PreflightAssessment:
    base = assess_resource(resource)
    collector = collector_for(resource).__class__.__name__
    allowed_use = resource.allowed_use.strip().lower()
    resource_type = resource.type.strip().lower()
    has_url = bool(resource.url.strip())

    special = special_preflight_assessment(
        resource=resource,
        collector=collector,
        base=base,
        allowed_use=allowed_use,
        resource_type=resource_type,
        has_url=has_url,
    )
    if special is not None:
        return special

    return PreflightAssessment(
        resource=resource,
        collector=collector,
        status=base.status,
        automation_eligible=False,
        reason=base.reason,
        next_step=fallback_next_step(base.status),
    )


def assess_preflight_resources(resources: list[Resource]) -> list[PreflightAssessment]:
    return [assess_preflight_resource(resource) for resource in resources]
