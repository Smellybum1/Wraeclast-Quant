from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.static_site_health_metadata import meta_content, optional_int
from wraeclast_quant.reports.static_site_health_models import (
    REQUIRED_STATIC_SITE_MARKERS,
    StaticSiteHealthResult,
)


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
        schema_version=meta_content(html, "wq:schema-version"),
        latest_run_id=optional_int(meta_content(html, "wq:latest-run-id")),
        size_bytes=path.stat().st_size,
    )


__all__ = [
    "REQUIRED_STATIC_SITE_MARKERS",
    "StaticSiteHealthResult",
    "check_static_site_health",
]
