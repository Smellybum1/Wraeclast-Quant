from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_doc_markdown_helpers import documented_bullets
from cli_public_intel_payload_helpers import public_intel_payload as _public_intel_payload


def write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(public_intel_payload()), encoding="utf-8")
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")
    return intel_path, site_dir


def write_publish_ready_bundle(
    tmp_path: Path,
    artifact_run_id: int | None = None,
    database_runs: int = 1,
) -> tuple[Path, Path, int]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    latest_run_id = 0
    for _ in range(database_runs):
        latest_run_id = repository.create_analysis_run(source_mode="sample-data", item_count=1).id
    run_id = artifact_run_id or latest_run_id
    intel_path = tmp_path / "public_intel.json"
    payload = public_intel_payload(run_id=run_id)
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    site_dir = tmp_path / "site"
    write_static_site(payload, site_dir)
    bundle_dir = tmp_path / "bundle"
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    return database_path, bundle_dir, latest_run_id


def public_intel_payload(run_id: int = 7) -> dict[str, object]:
    payload = _public_intel_payload(run_id=run_id)
    payload["recent_runs"] = []
    payload["top_opportunities"] = []
    payload["score_trends"] = []
    return payload


__all__ = [
    "documented_bullets",
    "public_intel_payload",
    "write_inputs",
    "write_publish_ready_bundle",
]
