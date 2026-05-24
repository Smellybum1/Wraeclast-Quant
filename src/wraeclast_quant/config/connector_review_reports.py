from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_approval_policy import connector_approval_helper
from wraeclast_quant.config.connector_policy_models import (
    ConnectorReview,
    ConnectorReviewReportResult,
)
from wraeclast_quant.config.connector_review_report_fetch import fetch_plan_for_report
from wraeclast_quant.config.connector_review_report_sections import connector_review_report_markdown
from wraeclast_quant.config.connector_review_checks import (
    check_connector_review,
    connector_review_status,
)
from wraeclast_quant.config.resources_loader import Resource


def connector_review_report(
    review: ConnectorReview,
    resources: list[Resource],
) -> ConnectorReviewReportResult:
    check = check_connector_review(review, resources)
    status = connector_review_status(review, resources)
    approval = connector_approval_helper(review, resources)
    fetch_plan = fetch_plan_for_report(review, resources)

    return ConnectorReviewReportResult(
        review=review,
        resource=check.resource,
        check_result=check,
        approval=approval,
        markdown=connector_review_report_markdown(
            review=review,
            check=check,
            status=status,
            approval=approval,
            fetch_plan=fetch_plan,
        ),
    )


def write_connector_review_report(
    review: ConnectorReview,
    resources: list[Resource],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    report = connector_review_report(review, resources)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.markdown, encoding="utf-8")
    return path
