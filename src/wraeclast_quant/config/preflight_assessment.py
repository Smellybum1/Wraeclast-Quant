from __future__ import annotations

from wraeclast_quant.collectors.registry import collector_for
from wraeclast_quant.config.compliance import assess_resource
from wraeclast_quant.config.preflight_models import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource


def assess_preflight_resource(resource: Resource) -> PreflightAssessment:
    base = assess_resource(resource)
    collector = collector_for(resource).__class__.__name__
    allowed_use = resource.allowed_use.strip().lower()
    resource_type = resource.type.strip().lower()
    has_url = bool(resource.url.strip())

    if resource_type == "discord":
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status="discord-gated",
            automation_eligible=False,
            reason="Discord requires explicit approved-bot/API compliance review.",
            next_step="Use manual summaries or complete approved-bot/API review first.",
        )

    if allowed_use in {"api", "rss", "download"} and not has_url:
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status="needs-review",
            automation_eligible=False,
            reason="Automation-marked resource is missing a URL.",
            next_step="Add the source URL and review terms, robots, auth, limits, and caching.",
        )

    if allowed_use in {"api", "rss", "download"} and has_url and base.automation_eligible:
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status=base.status,
            automation_eligible=True,
            reason=base.reason,
            next_step="Ready for source-specific connector design; keep dry-run until implemented.",
        )

    if base.status == "blocked":
        next_step = "Do not automate this source."
    elif base.status == "manual-review":
        next_step = "Keep this source manual-review only."
    else:
        next_step = "Clarify allowed use and review source terms before connector work."

    return PreflightAssessment(
        resource=resource,
        collector=collector,
        status=base.status,
        automation_eligible=False,
        reason=base.reason,
        next_step=next_step,
    )


def assess_preflight_resources(resources: list[Resource]) -> list[PreflightAssessment]:
    return [assess_preflight_resource(resource) for resource in resources]
