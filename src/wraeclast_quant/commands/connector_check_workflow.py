from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorCheckResult,
    ConnectorPolicyError,
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.resources_loader import load_resources


def build_connector_check_result(
    review_path: Path,
    resources_path: Path,
) -> ConnectorCheckResult:
    try:
        review = load_connector_review(review_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return check_connector_review(review, load_resources(resources_path))


__all__ = ["build_connector_check_result"]
