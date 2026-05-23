from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.static_site_health import (
    REQUIRED_STATIC_SITE_MARKERS,
    StaticSiteHealthResult,
    check_static_site_health,
)
from wraeclast_quant.reports.static_site_rendering import render_static_site

DEFAULT_SITE_DIR = Path("data/processed/site")


def load_public_intel(path: Path = DEFAULT_PUBLIC_INTEL_PATH) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_static_site(payload: dict[str, Any], output_dir: Path = DEFAULT_SITE_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(render_static_site(payload), encoding="utf-8")
    return output_path
