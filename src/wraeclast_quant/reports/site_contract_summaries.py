from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle import ARCHIVE_NAME, check_site_bundle_health
from wraeclast_quant.reports.static_site import check_static_site_health


def public_intel_summary(path: Path) -> dict[str, Any]:
    try:
        validation = validate_public_intel_file(path)
    except PublicIntelContractError as error:
        return {
            "valid": False,
            "schema_version": "",
            "latest_run_id": None,
            "top_opportunities": None,
            "alerts": None,
            "error": str(error),
        }
    return {
        "valid": validation.valid,
        "schema_version": validation.schema_version,
        "latest_run_id": validation.latest_run_id,
        "top_opportunities": validation.top_opportunities_count,
        "alerts": validation.alerts_count,
        "errors": validation.errors,
    }


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
