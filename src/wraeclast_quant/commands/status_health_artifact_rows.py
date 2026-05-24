from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifact_statuses import build_artifact_row_statuses
from wraeclast_quant.commands.status_health_artifacts import (
    market_brief_details,
    public_intel_details,
    site_bundle_details,
    static_site_details,
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
    row_statuses = build_artifact_row_statuses(context, intel_path=intel_path)
    strict_rows.extend(row_statuses.strict_rows())
    add_status_row(
        status_rows,
        "Market brief",
        row_statuses.market_brief,
        market_brief_details(brief_path, context.market_brief_health),
    )
    add_status_row(
        status_rows,
        "Public intel",
        row_statuses.public_intel,
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
        row_statuses.static_site,
        static_site_details(site_dir / "index.html", context.static_site_health, context.latest_run_id),
    )
    add_status_row(
        status_rows,
        "Site bundle",
        row_statuses.site_bundle,
        site_bundle_details(bundle_dir, context.site_bundle_health, context.latest_run_id),
    )


__all__ = ["add_artifact_rows"]
