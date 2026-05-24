from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_policy_models import ConnectorReviewPrepResult
from wraeclast_quant.config.connector_policy_utils import slug
from wraeclast_quant.config.connector_review_checklist import render_review_checklist
from wraeclast_quant.config.connector_review_draft import build_connector_review_draft
from wraeclast_quant.config.connector_review_io import write_connector_review_draft
from wraeclast_quant.config.resources_loader import Resource


def prepare_connector_review_workspace(
    resource_name: str,
    access_method: str,
    resources: list[Resource],
    output_dir: str | Path,
) -> ConnectorReviewPrepResult:
    review = build_connector_review_draft(resource_name, access_method, resources)
    output_path = Path(output_dir)
    review_path = output_path / f"{slug(review.resource_name)}_connector_review.json"
    checklist_path = output_path / f"{slug(review.resource_name)}_review_checklist.md"
    write_connector_review_draft(review, review_path)
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(
        render_review_checklist(review, review_path),
        encoding="utf-8",
    )
    next_commands = [
        f"wq connector-review-status --review-path {review_path}",
        f"wq connector-approval-helper --review-path {review_path}",
        f"wq connector-check --review-path {review_path}",
        f"wq connector-plan --review-path {review_path}",
    ]
    return ConnectorReviewPrepResult(
        review=review,
        review_path=review_path,
        checklist_path=checklist_path,
        next_commands=next_commands,
    )
