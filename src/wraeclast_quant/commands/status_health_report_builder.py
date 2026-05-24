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
from wraeclast_quant.commands.status_health_models import StatusHealthReport
from wraeclast_quant.commands.status_health_rows import add_status_row, strict_failure_keys
from wraeclast_quant.commands.status_health_storage import (
    backup_status,
    backup_status_details,
    database_health_details,
    database_health_status,
    exists_label,
    latest_run_empty_details,
)


def build_status_report_from_context(
    context: StatusHealthContext,
    *,
    database_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
) -> StatusHealthReport:
    status_rows: list[dict[str, str]] = []
    strict_rows: list[tuple[str, str]] = []
    add_status_row(
        status_rows,
        "Resources",
        "ok",
        f"{len(context.resources)} configured; {context.eligible_count} automation-eligible",
    )
    add_status_row(status_rows, "Database", exists_label(context.database_exists), str(database_path))

    database_health_row_status = database_health_status(context.database_health)
    strict_rows.append(("Database health", database_health_row_status))
    add_status_row(
        status_rows,
        "Database health",
        database_health_row_status,
        database_health_details(context.database_health),
    )
    _add_latest_run_rows(status_rows, context)
    _add_artifact_rows(
        status_rows,
        strict_rows,
        context,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
    )

    backup_row_status = backup_status(context.backups)
    strict_rows.append(("Backups", backup_row_status))
    add_status_row(status_rows, "Backups", backup_row_status, backup_status_details(context.backups))
    add_status_row(
        status_rows,
        "Safety boundary",
        "ok",
        "Local-only status check; collectors remain dry-run placeholders.",
    )
    strict_failures = [label for label, row_status in strict_rows if row_status == "needs attention"]
    return StatusHealthReport(
        rows=status_rows,
        strict_failures=strict_failures,
        strict_failure_keys=strict_failure_keys(strict_failures),
    )


def _add_latest_run_rows(status_rows: list[dict[str, str]], context: StatusHealthContext) -> None:
    if context.latest is None:
        add_status_row(status_rows, "Latest run", "none", latest_run_empty_details(context.database_health))
        add_status_row(status_rows, "Review coverage", "none", "No latest run.")
        return

    add_status_row(
        status_rows,
        "Latest run",
        "ok",
        (
            f"#{context.latest.id} {context.latest.source_mode}; "
            f"{context.latest.item_count} items; {context.latest.created_at}"
        ),
    )
    if context.coverage is not None:
        add_status_row(
            status_rows,
            "Review coverage",
            "ok",
            (
                f"{context.coverage.reviewed_recommendations}/"
                f"{context.coverage.total_recommendations} reviewed; "
                f"{context.coverage.reviewed_percent:.1f}%; "
                f"{context.coverage.unreviewed_recommendations} unreviewed"
            ),
        )


def _add_artifact_rows(
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
