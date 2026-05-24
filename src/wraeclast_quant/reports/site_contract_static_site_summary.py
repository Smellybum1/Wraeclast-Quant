from __future__ import annotations

from pathlib import Path
from typing import Any

from wraeclast_quant.reports.static_site import check_static_site_health


def static_site_summary(path: Path) -> dict[str, Any]:
    health = check_static_site_health(path)
    if health is None:
        return {
            "valid": False,
            "schema_version": "",
            "latest_run_id": None,
            "size_bytes": None,
            "errors": [f"{path.name} not found"],
        }
    return {
        "valid": health.valid,
        "schema_version": health.schema_version,
        "latest_run_id": health.latest_run_id,
        "size_bytes": health.size_bytes,
        "errors": [f"missing marker: {marker}" for marker in health.missing_markers],
    }


__all__ = ["static_site_summary"]
