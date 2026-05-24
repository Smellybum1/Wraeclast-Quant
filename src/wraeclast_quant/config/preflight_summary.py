from __future__ import annotations

from wraeclast_quant.config.preflight_models import PreflightAssessment, PreflightSummary


def summarize_preflight(assessments: list[PreflightAssessment]) -> PreflightSummary:
    return PreflightSummary(
        total=len(assessments),
        eligible=sum(1 for assessment in assessments if assessment.automation_eligible),
        manual_review=sum(1 for assessment in assessments if assessment.status == "manual-review"),
        needs_review=sum(1 for assessment in assessments if assessment.status == "needs-review"),
        blocked=sum(1 for assessment in assessments if assessment.status == "blocked"),
        discord_gated=sum(1 for assessment in assessments if assessment.status == "discord-gated"),
        placeholder_only=sum(1 for assessment in assessments if assessment.placeholder_only),
    )
