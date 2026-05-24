from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    ConnectorReviewReportResult,
    connector_review_report,
    load_connector_review,
    write_connector_review_report,
)
from wraeclast_quant.config.resources_loader import load_resources


@dataclass(frozen=True)
class ConnectorReviewReportWrite:
    report: ConnectorReviewReportResult
    written_path: Path


def write_connector_review_report_for_review(
    *,
    review_path: Path,
    output_path: Path,
    resources_path: Path,
) -> ConnectorReviewReportWrite:
    try:
        review = load_connector_review(review_path)
        resources = load_resources(resources_path)
        report = connector_review_report(review, resources)
        written_path = write_connector_review_report(review, resources, output_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return ConnectorReviewReportWrite(report=report, written_path=written_path)


__all__ = [
    "ConnectorReviewReportWrite",
    "write_connector_review_report_for_review",
]
