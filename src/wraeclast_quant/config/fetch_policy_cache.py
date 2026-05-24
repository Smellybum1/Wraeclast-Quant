from __future__ import annotations

import hashlib
import re
from pathlib import Path

from wraeclast_quant.config.resources_loader import Resource


def cache_path_for(resource: Resource, cache_root: Path) -> Path:
    safe_name = _safe_slug(resource.name or resource.id or "resource")
    digest = hashlib.sha256(resource.url.encode("utf-8")).hexdigest()[:12]
    return cache_root / f"{safe_name}-{digest}.cache"


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug[:60] or "resource"
