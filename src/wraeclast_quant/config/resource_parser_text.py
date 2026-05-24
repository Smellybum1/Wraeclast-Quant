from __future__ import annotations

import html
import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_ -]+)\s*:\s*(.*?)\s*$")


def clean_line(line: str) -> str:
    cleaned = html.unescape(line)
    cleaned = cleaned.lstrip("\ufeff")
    cleaned = cleaned.replace("\\#", "#").replace("\\-", "-").replace("\\_", "_")
    return cleaned.rstrip()


def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def join_notes(existing: str, extra: str) -> str:
    if not existing:
        return extra
    return f"{existing} {extra}"


def is_non_resource_section(section: str) -> bool:
    return section.strip().lower() in {"rules", "field guide"}
