from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_context import load_status_health_context
from wraeclast_quant.commands.status_health_models import (
    STATUS_JSON_SCHEMA_VERSION,
    StatusHealthReport,
)
from wraeclast_quant.commands.status_health_report_builder import build_status_report_from_context
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def build_status_report(
    *,
    database_path: Path = DEFAULT_DATABASE_PATH,
    resources_path: Path = Path("RESOURCES.md"),
    brief_path: Path = Path("data/processed/market_brief.md"),
    intel_path: Path = DEFAULT_PUBLIC_INTEL_PATH,
    site_dir: Path = DEFAULT_SITE_DIR,
    bundle_dir: Path = DEFAULT_SITE_BUNDLE_DIR,
    backup_dir: Path = DEFAULT_BACKUP_DIR,
) -> StatusHealthReport:
    context = load_status_health_context(
        database_path=database_path,
        resources_path=resources_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        backup_dir=backup_dir,
    )
    return build_status_report_from_context(
        context,
        database_path=database_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
    )
