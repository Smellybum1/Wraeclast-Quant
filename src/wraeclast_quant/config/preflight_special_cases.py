from __future__ import annotations

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.config.preflight_models import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource


AUTOMATION_ALLOWED_USES = {"api", "rss", "download"}


def special_preflight_assessment(
    *,
    resource: Resource,
    collector: str,
    base: ComplianceAssessment,
    allowed_use: str,
    resource_type: str,
    has_url: bool,
) -> PreflightAssessment | None:
    if resource_type == "discord":
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status="discord-gated",
            automation_eligible=False,
            reason="Discord requires explicit approved-bot/API compliance review.",
            next_step="Use manual summaries or complete approved-bot/API review first.",
        )

    if allowed_use in AUTOMATION_ALLOWED_USES and not has_url:
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status="needs-review",
            automation_eligible=False,
            reason="Automation-marked resource is missing a URL.",
            next_step="Add the source URL and review terms, robots, auth, limits, and caching.",
        )

    if allowed_use in AUTOMATION_ALLOWED_USES and has_url and base.automation_eligible:
        return PreflightAssessment(
            resource=resource,
            collector=collector,
            status=base.status,
            automation_eligible=True,
            reason=base.reason,
            next_step="Ready for source-specific connector design; keep dry-run until implemented.",
        )

    return None


__all__ = [
    "AUTOMATION_ALLOWED_USES",
    "special_preflight_assessment",
]
