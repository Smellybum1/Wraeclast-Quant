from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.site_bundle_manifest import manifest_errors


def load_health_manifest(manifest_path: Path) -> tuple[dict[str, Any], list[str]]:
    if not manifest_path.exists():
        return {}, ["manifest.json is missing"]

    try:
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {}, [f"manifest.json is invalid JSON: {error.msg}"]

    if not isinstance(loaded, dict):
        return {}, ["manifest.json must be a JSON object"]

    return loaded, manifest_errors(loaded)


def optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = ["load_health_manifest", "optional_int"]
