from __future__ import annotations

from wraeclast_quant.config.resource_models import Resource
from wraeclast_quant.config.resource_parser_builders import build_resource
from wraeclast_quant.config.resource_parser_bullets import parse_bullet
from wraeclast_quant.config.resource_parser_tables import parse_table
from wraeclast_quant.config.resource_parser_text import (
    BULLET_RE,
    HEADING_RE,
    KEY_VALUE_RE,
    clean_line,
    is_non_resource_section,
    join_notes,
    normalize_key,
)


def parse_resources_markdown(markdown: str) -> list[Resource]:
    lines = [clean_line(line) for line in markdown.splitlines()]
    resources: list[Resource] = []
    section = ""
    current: dict[str, str] | None = None

    def flush() -> None:
        nonlocal current
        if current and (current.get("name") or current.get("url")):
            resources.append(build_resource(current, section))
        current = None

    table_rows: list[str] = []

    for line in lines:
        if not line.strip():
            continue

        heading = HEADING_RE.match(line.strip())
        if heading:
            flush()
            resources.extend(parse_table(table_rows, section))
            table_rows = []
            section = heading.group(2).strip() if len(heading.group(1)) >= 2 else ""
            continue

        if line.strip().startswith("|"):
            if is_non_resource_section(section):
                continue
            flush()
            table_rows.append(line.strip())
            continue

        if table_rows:
            resources.extend(parse_table(table_rows, section))
            table_rows = []

        bullet = BULLET_RE.match(line)
        if bullet:
            if not section or is_non_resource_section(section):
                continue
            flush()
            current = parse_bullet(bullet.group(1))
            continue

        key_value = KEY_VALUE_RE.match(line)
        if key_value and current is not None:
            key = normalize_key(key_value.group(1))
            current[key] = key_value.group(2).strip()
            continue

        if current is not None:
            current["notes"] = join_notes(current.get("notes", ""), line.strip())

    flush()
    if table_rows:
        resources.extend(parse_table(table_rows, section))

    return resources


__all__ = ["parse_resources_markdown"]
