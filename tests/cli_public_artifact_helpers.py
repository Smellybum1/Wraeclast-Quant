from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository


def write_manual_resources(tmp_path: Path) -> Path:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(
        """
## Official Sources
- name: Manual Source
  url: https://example.test/manual
  allowed_use: manual-review
""",
        encoding="utf-8",
    )
    return resources_path


def database_with_two_runs(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=1)
    repository.create_analysis_run(source_mode="sample-data", item_count=1)
    return database_path


def status_json_args(
    tmp_path: Path,
    *,
    database_path: Path,
    resources_path: Path,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    bundle_dir: Path | None = None,
) -> list[str]:
    return [
        "status",
        "--json",
        "--database-path",
        str(database_path),
        "--resources-path",
        str(resources_path),
        "--brief-path",
        str(tmp_path / "missing.md"),
        "--intel-path",
        str(intel_path or tmp_path / "missing.json"),
        "--site-dir",
        str(site_dir or tmp_path / "missing_site"),
        "--bundle-dir",
        str(bundle_dir or tmp_path / "missing_bundle"),
        "--backup-dir",
        str(tmp_path / "missing_backups"),
    ]


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
        "recent_runs": [
            {
                "id": run_id,
                "created_at": "2026-05-23T00:00:00+00:00",
                "source_mode": "sample-data",
                "item_count": 1,
            }
        ],
        "top_opportunities": [
            {
                "item_name": "Stormglass Catalyst",
                "opportunity_score": 70.4,
                "action": "WATCH",
            }
        ],
        "score_trends": [
            {
                "item_name": "Stormglass Catalyst",
                "points": [{"run_id": run_id, "score": 70.4, "action": "WATCH"}],
            }
        ],
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
