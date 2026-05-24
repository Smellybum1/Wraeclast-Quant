from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    ConnectorReview,
    load_connector_review,
)
from wraeclast_quant.config.fetch_policy import FetchPlanResult, build_fetch_plan
from wraeclast_quant.config.resources_loader import load_resources


@dataclass(frozen=True)
class ConnectorPlanWorkflowResult:
    review: ConnectorReview
    result: FetchPlanResult


def build_connector_plan_result(
    review_path: Path,
    resources_path: Path,
) -> ConnectorPlanWorkflowResult:
    try:
        review = load_connector_review(review_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return ConnectorPlanWorkflowResult(
        review=review,
        result=build_fetch_plan(review, load_resources(resources_path)),
    )


__all__ = [
    "ConnectorPlanWorkflowResult",
    "build_connector_plan_result",
]
