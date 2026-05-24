from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifacts import (
    fresh_artifact_status,
    market_brief_details,
    market_brief_status,
    public_intel_details,
    public_intel_run_id,
    public_intel_status,
    site_bundle_details,
    site_bundle_run_id,
    site_bundle_status,
    static_site_details,
    static_site_run_id,
    static_site_status,
)
from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row


def add_artifact_rows(
    status_rows: list[dict[str, str]],
    strict_rows: list[tuple[str, str]],
    context: StatusHealthContext,
    *,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
) -> None:
    market_brief_row_status = market_brief_status(context.market_brief_health)
    public_intel_row_status = fresh_artifact_status(
        public_intel_status(intel_path, context.intel_validation, context.intel_error),
        public_intel_run_id(context.intel_validation),
        context.latest_run_id,
    )
    static_site_row_status = fresh_artifact_status(
        static_site_status(context.static_site_health),
        static_site_run_id(context.static_site_health),
        context.latest_run_id,
    )
    site_bundle_row_status = fresh_artifact_status(
        site_bundle_status(context.site_bundle_health),
        site_bundle_run_id(context.site_bundle_health),
        context.latest_run_id,
    )
    strict_rows.extend(
        [
            ("Market brief", market_brief_row_status),
            ("Public intel", public_intel_row_status),
            ("Static site", static_site_row_status),
            ("Site bundle", site_bundle_row_status),
        ]
    )
    add_status_row(
        status_rows,
        "Market brief",
        market_brief_row_status,
        market_brief_details(brief_path, context.market_brief_health),
    )
    add_status_row(
        status_rows,
        "Public intel",
        public_intel_row_status,
        public_intel_details(
            intel_path,
            context.intel_validation,
            context.intel_error,
            context.latest_run_id,
        ),
    )
    add_status_row(
        status_rows,
        "Static site",
        static_site_row_status,
        static_site_details(site_dir / "index.html", context.static_site_health, context.latest_run_id),
    )
    add_status_row(
        status_rows,
        "Site bundle",
        site_bundle_row_status,
        site_bundle_details(bundle_dir, context.site_bundle_health, context.latest_run_id),
    )
