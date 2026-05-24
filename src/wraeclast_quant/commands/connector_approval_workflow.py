from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorApprovalHelperResult,
    ConnectorApprovalPatchResult,
    ConnectorPolicyError,
    connector_approval_helper,
    connector_approval_patch,
    load_connector_review,
    write_connector_approval_patch,
)
from wraeclast_quant.config.resources_loader import load_resources


@dataclass(frozen=True)
class ConnectorApprovalPatchWorkflowResult:
    result: ConnectorApprovalPatchResult
    written_path: Path | None


def build_connector_approval_helper_result(
    review_path: Path,
    resources_path: Path,
) -> ConnectorApprovalHelperResult:
    try:
        review = load_connector_review(review_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return connector_approval_helper(review, load_resources(resources_path))


def build_connector_approval_patch_result(
    review_path: Path,
    output_path: Path,
    resources_path: Path,
) -> ConnectorApprovalPatchWorkflowResult:
    try:
        review = load_connector_review(review_path)
        resources_markdown = resources_path.read_text(encoding="utf-8")
        resources = load_resources(resources_path)
        result = connector_approval_patch(
            review,
            resources,
            resources_markdown,
            str(resources_path),
        )
        if result.patch_available:
            written_path = write_connector_approval_patch(
                review,
                resources,
                resources_markdown,
                output_path,
                str(resources_path),
            )
        else:
            written_path = None
    except OSError as error:
        raise typer.BadParameter(f"Could not read resources file: {error}") from error
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return ConnectorApprovalPatchWorkflowResult(
        result=result,
        written_path=written_path,
    )


__all__ = [
    "ConnectorApprovalPatchWorkflowResult",
    "build_connector_approval_helper_result",
    "build_connector_approval_patch_result",
]
