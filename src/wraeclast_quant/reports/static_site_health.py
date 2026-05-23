from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_STATIC_SITE_MARKERS = {
    "title": "<title>Wraeclast Quant</title>",
    "heading": "<h1>Wraeclast Quant</h1>",
    "schema-version": 'name="wq:schema-version"',
    "generated-at": 'name="wq:generated-at"',
    "latest-run-id": 'name="wq:latest-run-id"',
}


@dataclass(frozen=True)
class StaticSiteHealthResult:
    path: Path
    valid: bool
    missing_markers: list[str]
    schema_version: str
    latest_run_id: int | None
    size_bytes: int


def check_static_site_health(path: Path) -> StaticSiteHealthResult | None:
    if not path.exists():
        return None
    html = path.read_text(encoding="utf-8")
    missing_markers = [
        name
        for name, marker in sorted(REQUIRED_STATIC_SITE_MARKERS.items())
        if marker not in html
    ]
    return StaticSiteHealthResult(
        path=path,
        valid=not missing_markers,
        missing_markers=missing_markers,
        schema_version=_meta_content(html, "wq:schema-version"),
        latest_run_id=_optional_int(_meta_content(html, "wq:latest-run-id")),
        size_bytes=path.stat().st_size,
    )


def _meta_content(html: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)">',
        html,
        re.IGNORECASE,
    )
    return match.group(1) if match else ""


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
