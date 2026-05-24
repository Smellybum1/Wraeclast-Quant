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
from cli_public_intel_payload_helpers import public_intel_payload
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


__all__ = [
    "StatusWorkspace",
    "status_workspace",
    "write_manual_resources",
]
