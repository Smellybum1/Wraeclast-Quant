from __future__ import annotations

from typing import Any

from wraeclast_quant.config.compliance import ComplianceAssessment
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def review_coverage_payload(
    repository: SnapshotRepository,
    latest: AnalysisRunRecord,
) -> dict[str, Any]:
    coverage = repository.review_coverage_for_run(latest.id)
    return {
        "run_id": coverage.run_id,
        "total_recommendations": coverage.total_recommendations,
        "reviewed_recommendations": coverage.reviewed_recommendations,
        "unreviewed_recommendations": coverage.unreviewed_recommendations,
        "reviewed_percent": round(coverage.reviewed_percent, 1),
    }


def compliance_summary(
    assessments: list[ComplianceAssessment],
    total_resources: int,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    automation_eligible_count = 0
    for assessment in assessments:
        status_counts[assessment.status] = status_counts.get(assessment.status, 0) + 1
        if assessment.automation_eligible:
            automation_eligible_count += 1
    return {
        "total_resources": total_resources,
        "status_counts": dict(sorted(status_counts.items())),
        "automation_eligible_count": automation_eligible_count,
    }
