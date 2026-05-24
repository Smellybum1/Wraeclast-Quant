from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    ConnectorReviewPrepResult,
    build_connector_review_draft,
    prepare_connector_review_workspace,
    write_connector_review_draft,
)
from wraeclast_quant.config.resources_loader import load_resources


@dataclass(frozen=True)
class ConnectorReviewDraftWrite:
    written_path: Path


def write_connector_review_draft_for_resource(
    *,
    resource: str,
    access_method: str,
    output_path: Path,
    resources_path: Path,
) -> ConnectorReviewDraftWrite:
    try:
        review = build_connector_review_draft(
            resource_name=resource,
            access_method=access_method,
            resources=load_resources(resources_path),
        )
        written_path = write_connector_review_draft(review, output_path)
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error

    return ConnectorReviewDraftWrite(written_path=written_path)


def prepare_connector_review_for_resource(
    *,
    resource: str,
    access_method: str,
    resources_path: Path,
    output_dir: Path,
) -> ConnectorReviewPrepResult:
    try:
        return prepare_connector_review_workspace(
            resource_name=resource,
            access_method=access_method,
            resources=load_resources(resources_path),
            output_dir=output_dir,
        )
    except ConnectorPolicyError as error:
        raise typer.BadParameter(str(error)) from error


__all__ = [
    "ConnectorReviewDraftWrite",
    "prepare_connector_review_for_resource",
    "write_connector_review_draft_for_resource",
]
