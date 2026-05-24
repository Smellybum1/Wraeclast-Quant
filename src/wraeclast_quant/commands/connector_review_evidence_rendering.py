from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_review_evidence_workflow import (
    ConnectorReviewEvidenceUpdate,
)
from wraeclast_quant.commands.connector_review_status_rendering import print_connector_review_status
from wraeclast_quant.config.connector_policy import connector_review_status
from wraeclast_quant.config.resources_loader import Resource


def print_connector_review_evidence_update(
    update: ConnectorReviewEvidenceUpdate,
    *,
    review_path: Path,
    resources: list[Resource],
) -> None:
    console.print(f"Updated connector review evidence in {review_path}")
    print_connector_review_status(connector_review_status(update.review, resources))
    console.print(
        "Evidence update is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector."
    )


__all__ = ["print_connector_review_evidence_update"]
