from __future__ import annotations

import re
from difflib import unified_diff

from wraeclast_quant.config.connector_policy_models import ConnectorPolicyError
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


def find_resource_block(lines: list[str], resource: Resource) -> tuple[int, int] | None:
    matches: list[tuple[int, int]] = []
    start = None
    for index, line in enumerate(lines):
        if is_resource_bullet(line):
            if start is not None:
                append_matching_block(matches, lines, start, index, resource)
            start = index
    if start is not None:
        append_matching_block(matches, lines, start, len(lines), resource)
    if len(matches) != 1:
        return None
    return matches[0]


def append_matching_block(
    matches: list[tuple[int, int]],
    lines: list[str],
    start: int,
    end: int,
    resource: Resource,
) -> None:
    fields = block_fields(lines[start:end])
    if resource.id and fields.get("id", "").casefold() == resource.id.casefold():
        matches.append((start, end))
        return
    if fields.get("name", "").casefold() == resource.name.casefold():
        matches.append((start, end))


def block_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        cleaned = clean_resource_line(line).strip()
        if cleaned.startswith("- "):
            cleaned = cleaned[2:].strip()
        match = re.match(r"([A-Za-z_ -]+)\s*:\s*(.*?)\s*$", cleaned)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
            fields[key] = match.group(2).strip()
    return fields


def is_resource_bullet(line: str) -> bool:
    cleaned = clean_resource_line(line).lstrip()
    return cleaned.startswith("- ")


def clean_resource_line(line: str) -> str:
    cleaned = line.rstrip("\r\n")
    cleaned = cleaned.replace("&#x20;", " ")
    cleaned = cleaned.replace("\\-", "-").replace("\\_", "_")
    return cleaned
