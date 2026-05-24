from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_public_intel_payload_helpers import public_intel_payload


def write_publish_ready_bundle(tmp_path: Path) -> tuple[Path, Path, int]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    payload = public_intel_payload(run_id=run.id)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    site_dir = tmp_path / "site"
    write_static_site(payload, site_dir)
    bundle_dir = tmp_path / "bundle"
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    return database_path, bundle_dir, run.id


def write_public_intel_file(
    tmp_path: Path,
    payload: dict[str, object] | None = None,
) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(payload or public_intel_payload()), encoding="utf-8")
    return intel_path


def write_public_intel_with_raw_inputs(tmp_path: Path) -> Path:
    payload = public_intel_payload(run_id=1)
    payload["top_opportunities"] = [
        {"item_name": "Bad", "inputs": {"demand_momentum": 1}},
    ]
    return write_public_intel_file(tmp_path, payload)


def write_public_intel_missing_schema(tmp_path: Path) -> Path:
    payload = public_intel_payload()
    del payload["schema_version"]
    return write_public_intel_file(tmp_path, payload)


def write_minimal_invalid_public_intel(tmp_path: Path) -> Path:
    return write_public_intel_file(tmp_path, {"latest_run": {"id": 7}})


def write_minimal_static_site(tmp_path: Path) -> Path:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")
    return site_dir


__all__ = [
    "write_minimal_invalid_public_intel",
    "write_minimal_static_site",
    "write_public_intel_file",
    "write_public_intel_missing_schema",
    "write_public_intel_with_raw_inputs",
    "write_publish_ready_bundle",
]
