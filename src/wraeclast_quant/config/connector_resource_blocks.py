from __future__ import annotations

import re

from wraeclast_quant.config.resources_loader import Resource


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
