from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_approval_patch_builder import connector_approval_patch
from wraeclast_quant.config.connector_policy_models import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


def write_connector_approval_patch(
    review: ConnectorReview,
    resources: list[Resource],
    resources_markdown: str,
    output_path: str | Path,
    resources_label: str = "RESOURCES.md",
) -> Path:
    result = connector_approval_patch(review, resources, resources_markdown, resources_label)
    if not result.patch_available:
        raise ConnectorPolicyError(result.reason)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.patch_text, encoding="utf-8")
    return path


__all__ = ["write_connector_approval_patch"]
