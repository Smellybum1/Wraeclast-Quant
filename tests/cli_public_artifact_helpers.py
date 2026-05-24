from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity
from cli_snapshot_helpers import save_scored_run


@dataclass(frozen=True)
class StatusWorkspace:
    database_path: Path
    resources_path: Path
    brief_path: Path
    intel_path: Path
    site_dir: Path
    bundle_dir: Path
    backup_dir: Path


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


def status_workspace(tmp_path: Path) -> StatusWorkspace:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(
        """
## Official Sources
- name: Approved API
  type: official
  url: https://example.test/api
  allowed_use: api
""",
        encoding="utf-8",
    )
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = save_scored_run(
        repository,
        [
            opportunity("Reviewed Catalyst", 76.0, "BUY"),
            opportunity("Open Catalyst", 60.0, "WATCH"),
        ],
    )
    repository.save_recommendation_outcome(run.id, "Reviewed Catalyst", "positive")
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    bundle_dir = tmp_path / "site_bundle"
    backup_dir = tmp_path / "backups"
    write_market_brief(
        [opportunity("Reviewed Catalyst", 76.0, "BUY")],
        path=brief_path,
    )
    intel_payload = public_intel_payload(run_id=run.id)
    intel_path.write_text(json.dumps(intel_payload), encoding="utf-8")
    write_static_site(intel_payload, site_dir)
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-24T00:00:00+00:00",
    )
    return StatusWorkspace(
        database_path=database_path,
        resources_path=resources_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        backup_dir=backup_dir,
    )


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
    return status_args(
        tmp_path,
        database_path=database_path,
        resources_path=resources_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        json_output=True,
    )


def status_args(
    tmp_path: Path,
    *,
    database_path: Path,
    resources_path: Path,
    brief_path: Path | None = None,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    bundle_dir: Path | None = None,
    backup_dir: Path | None = None,
    strict: bool = False,
    json_output: bool = False,
) -> list[str]:
    args = ["status"]
    if strict:
        args.append("--strict")
    if json_output:
        args.append("--json")
    return [
        *args,
        "--database-path",
        str(database_path),
        "--resources-path",
        str(resources_path),
        "--brief-path",
        str(brief_path or tmp_path / "missing.md"),
        "--intel-path",
        str(intel_path or tmp_path / "missing.json"),
        "--site-dir",
        str(site_dir or tmp_path / "missing_site"),
        "--bundle-dir",
        str(bundle_dir or tmp_path / "missing_bundle"),
        "--backup-dir",
        str(backup_dir or tmp_path / "missing_backups"),
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


__all__ = [
    "StatusWorkspace",
    "database_with_two_runs",
    "public_intel_payload",
    "status_args",
    "status_json_args",
    "status_workspace",
    "write_invalid_market_brief",
    "write_invalid_public_intel",
    "write_invalid_site_bundle",
    "write_invalid_static_site",
    "write_manual_resources",
    "write_publish_ready_bundle",
]
