from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.site_bundle import ARCHIVE_NAME, check_site_bundle_health


def bundle_summary(bundle_dir: Path) -> dict[str, Any]:
    health = check_site_bundle_health(bundle_dir)
    if health is None:
        return {
            "valid": False,
            "bundle_type": "",
            "public_intel_schema_version": "",
            "latest_run_id": None,
            "archive": {"name": ARCHIVE_NAME, "size_bytes": None},
            "files": [],
            "errors": [f"{ARCHIVE_NAME} not found"],
        }

    manifest = load_manifest(bundle_dir / "manifest.json")
    return {
        "valid": health.valid,
        "bundle_type": str(manifest.get("bundle_type", "")),
        "public_intel_schema_version": health.schema_version,
        "latest_run_id": health.latest_run_id,
        "archive": {
            "name": ARCHIVE_NAME,
            "size_bytes": health.archive_size_bytes,
        },
        "files": [
            {
                "path": str(file_info.get("path", "")),
                "size_bytes": file_info.get("size_bytes"),
            }
            for file_info in manifest.get("files", [])
            if isinstance(file_info, dict)
        ],
        "errors": health.errors,
    }


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


__all__ = ["bundle_summary", "load_manifest"]
