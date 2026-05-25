from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository


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
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": run_id,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        "recent_runs": [],
        "top_opportunities": [],
        "score_trends": [],
        "snapshot_changes": {
            "previous_run_id": None,
            "latest_run_id": run_id,
            "top_movers": [],
            "status_changes": [],
        },
        "alerts": [],
        "outcome_summary": {"positive": 0, "neutral": 0, "negative": 0},
        "review_coverage": {
            "run_id": run_id,
            "total_recommendations": 1,
            "reviewed_recommendations": 0,
            "unreviewed_recommendations": 1,
            "reviewed_percent": 0.0,
        },
        "compliance_summary": {
            "total_resources": 1,
            "status_counts": {"manual-review": 1},
            "automation_eligible_count": 0,
        },
    }


def documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }


__all__ = [
    "documented_bullets",
    "public_intel_payload",
    "write_inputs",
    "write_publish_ready_bundle",
]
