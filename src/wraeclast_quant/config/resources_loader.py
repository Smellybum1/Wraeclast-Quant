from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel


class Resource(BaseModel):
    id: str = ""
    name: str
    url: str = ""
    type: str = "unknown"
    priority: str = "medium"
    allowed_use: str = "manual-review"
    collector: str = ""
    refresh: str = ""
    reliability: str = "unknown"
    notes: str = ""
    section: str = ""


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_ -]+)\s*:\s*(.*?)\s*$")
_URL_RE = re.compile(r"https?://\S+")


def load_resources(path: str | Path = "RESOURCES.md") -> list[Resource]:
    resource_path = Path(path)
    return parse_resources_markdown(resource_path.read_text(encoding="utf-8"))


def parse_resources_markdown(markdown: str) -> list[Resource]:
    lines = [_clean_line(line) for line in markdown.splitlines()]
    resources: list[Resource] = []
    section = ""
    current: dict[str, str] | None = None

    def flush() -> None:
        nonlocal current
        if current and (current.get("name") or current.get("url")):
            resources.append(_build_resource(current, section))
        current = None

    table_rows: list[str] = []

    for line in lines:
        if not line.strip():
            continue

        heading = _HEADING_RE.match(line.strip())
        if heading:
            flush()
            resources.extend(_parse_table(table_rows, section))
            table_rows = []
            section = heading.group(2).strip() if len(heading.group(1)) >= 2 else ""
            continue

        if line.strip().startswith("|"):
            if _is_non_resource_section(section):
                continue
            flush()
            table_rows.append(line.strip())
            continue

        if table_rows:
            resources.extend(_parse_table(table_rows, section))
            table_rows = []

        bullet = _BULLET_RE.match(line)
        if bullet:
            if not section or _is_non_resource_section(section):
                continue
            flush()
            current = _parse_bullet(bullet.group(1))
            continue

        key_value = _KEY_VALUE_RE.match(line)
        if key_value and current is not None:
            key = _normalize_key(key_value.group(1))
            current[key] = key_value.group(2).strip()
            continue

        if current is not None:
            current["notes"] = _join_notes(current.get("notes", ""), line.strip())

    flush()
    if table_rows:
        resources.extend(_parse_table(table_rows, section))

    return resources


def _clean_line(line: str) -> str:
    cleaned = html.unescape(line)
    cleaned = cleaned.lstrip("\ufeff")
    cleaned = cleaned.replace("\\#", "#").replace("\\-", "-").replace("\\_", "_")
    return cleaned.rstrip()


def _parse_bullet(text: str) -> dict[str, str]:
    if text.lstrip().startswith("#"):
        return {}

    key_value = _KEY_VALUE_RE.match(text)
    if key_value:
        return {_normalize_key(key_value.group(1)): key_value.group(2).strip()}

    link = _LINK_RE.search(text)
    if link:
        return {"name": link.group(1).strip(), "url": link.group(2).strip()}

    url = _URL_RE.search(text)
    if url:
        name = text.replace(url.group(0), "").strip(" -:")
        return {"name": name or url.group(0), "url": url.group(0)}

    return {"name": text.strip()}


def _parse_table(rows: Iterable[str], section: str) -> list[Resource]:
    row_list = [row for row in rows if row.strip()]
    if len(row_list) < 2:
        return []

    headers = [_normalize_key(cell) for cell in _split_table_row(row_list[0])]
    parsed: list[Resource] = []
    for row in row_list[2:]:
        cells = _split_table_row(row)
        if len(cells) != len(headers):
            continue
        data = dict(zip(headers, cells, strict=True))
        if data.get("name") or data.get("url"):
            parsed.append(_build_resource(data, section))
    return parsed


def _split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _build_resource(data: dict[str, str], section: str) -> Resource:
    url = data.get("url", "")
    name = data.get("name") or _name_from_url(url) or "Unnamed resource"
    resource_type = data.get("type") or infer_resource_type(section, url, name)
    return Resource(
        id=(data.get("id") or "").strip(),
        name=name.strip(),
        url=url.strip(),
        type=resource_type.strip() or "unknown",
        priority=(data.get("priority") or "medium").strip() or "medium",
        allowed_use=(data.get("allowed_use") or "manual-review").strip() or "manual-review",
        collector=(data.get("collector") or "").strip(),
        refresh=(data.get("refresh") or "").strip(),
        reliability=(data.get("reliability") or "unknown").strip() or "unknown",
        notes=(data.get("notes") or "").strip(),
        section=section.strip(),
    )


def infer_resource_type(section: str = "", url: str = "", name: str = "") -> str:
    text = f"{section} {url} {name}".lower()
    if "price" in text or "economy" in text or "poe2scout" in text:
        return "price_site"
    if "build" in text or "maxroll" in text or "mobalytics" in text:
        return "build_site"
    if "reddit" in text or "social" in text:
        return "social"
    if "youtube" in text or "video" in text:
        return "youtube"
    if "official" in text or "patch" in text or "pathofexile.com/forum" in text:
        return "official"
    return "unknown"


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def _name_from_url(url: str) -> str:
    if not url:
        return ""
    return url.removeprefix("https://").removeprefix("http://").split("/")[0]


def _join_notes(existing: str, extra: str) -> str:
    if not existing:
        return extra
    return f"{existing} {extra}"


def _is_non_resource_section(section: str) -> bool:
    return section.strip().lower() in {"rules", "field guide"}
