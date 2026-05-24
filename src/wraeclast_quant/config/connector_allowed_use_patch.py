from __future__ import annotations

from difflib import unified_diff

from wraeclast_quant.config.connector_policy_models import ConnectorPolicyError
from wraeclast_quant.config.connector_resource_blocks import clean_resource_line, find_resource_block
from wraeclast_quant.config.resources_loader import Resource


def allowed_use_patch(
    markdown: str,
    resource: Resource,
    replacement_value: str,
    resources_label: str,
) -> str:
    lines = markdown.splitlines(keepends=True)
    block = find_resource_block(lines, resource)
    if block is None:
        raise ConnectorPolicyError(
            "Could not confidently locate the matching resource block in RESOURCES.md."
        )
    start, end = block
    allowed_use_indexes = [
        index
        for index in range(start, end)
        if clean_resource_line(lines[index]).strip().casefold().startswith("allowed_use:")
    ]
    if len(allowed_use_indexes) != 1:
        raise ConnectorPolicyError(
            "Could not confidently locate exactly one allowed_use line for this resource."
        )

    allowed_use_index = allowed_use_indexes[0]
    original_line = lines[allowed_use_index]
    newline = "\r\n" if original_line.endswith("\r\n") else "\n" if original_line.endswith("\n") else ""
    key_prefix = original_line.rstrip("\r\n").split(":", 1)[0]
    updated = lines.copy()
    updated[allowed_use_index] = f"{key_prefix}: {replacement_value}{newline}"
    diff = "".join(
        unified_diff(
            lines,
            updated,
            fromfile=resources_label,
            tofile=resources_label,
            n=0,
            lineterm="",
        )
    )
    if not diff.strip():
        raise ConnectorPolicyError("No approval patch is needed.")
    return diff
