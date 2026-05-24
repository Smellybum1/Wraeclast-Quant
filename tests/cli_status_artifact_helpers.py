from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site

from cli_public_intel_payload_helpers import public_intel_payload


def write_invalid_public_intel(tmp_path: Path) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{}", encoding="utf-8")
    return intel_path


def write_invalid_market_brief(tmp_path: Path) -> Path:
    brief_path = tmp_path / "market_brief.md"
    brief_path.write_text("# Wrong Report", encoding="utf-8")
    return brief_path


def write_invalid_static_site(tmp_path: Path) -> Path:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><title>Other</title></html>", encoding="utf-8")
    return site_dir


def write_invalid_site_bundle(tmp_path: Path) -> Path:
    bundle_dir = tmp_path / "site_bundle"
    bundle_dir.mkdir()
    (bundle_dir / "wraeclast_quant_site_bundle.zip").write_bytes(b"not a zip")
    return bundle_dir


def write_stale_public_intel(tmp_path: Path, run_id: int = 1) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(public_intel_payload(run_id=run_id)), encoding="utf-8")
    return intel_path


def write_stale_static_site(tmp_path: Path, run_id: int = 1) -> Path:
    site_dir = tmp_path / "site"
    write_static_site(public_intel_payload(run_id=run_id), site_dir)
    return site_dir


def write_stale_site_bundle(tmp_path: Path, run_id: int = 1) -> Path:
    intel_path = tmp_path / "bundle_source_intel.json"
    site_dir = tmp_path / "bundle_source_site"
    bundle_dir = tmp_path / "site_bundle"
    stale_payload = public_intel_payload(run_id=run_id)
    intel_path.write_text(json.dumps(stale_payload), encoding="utf-8")
    write_static_site(stale_payload, site_dir)
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    return bundle_dir


__all__ = [
    "write_invalid_market_brief",
    "write_invalid_public_intel",
    "write_invalid_site_bundle",
    "write_invalid_static_site",
    "write_stale_public_intel",
    "write_stale_site_bundle",
    "write_stale_static_site",
]
