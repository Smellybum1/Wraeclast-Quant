from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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


__all__ = ["REQUIRED_STATIC_SITE_MARKERS", "StaticSiteHealthResult"]
