from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.commands.status_health_artifact_statuses import ArtifactRowStatuses
from wraeclast_quant.commands.status_health_artifacts import (
    market_brief_details,
    public_intel_details,
    site_bundle_details,
    static_site_details,
)
from wraeclast_quant.commands.status_health_context import StatusHealthContext


@dataclass(frozen=True)
class ArtifactStatusRow:
    label: str
    status: str
    details: str


def artifact_status_rows(
    context: StatusHealthContext,
    *,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
    row_statuses: ArtifactRowStatuses,
) -> list[ArtifactStatusRow]:
    return [
        ArtifactStatusRow(
            "Market brief",
            row_statuses.market_brief,
            market_brief_details(brief_path, context.market_brief_health),
        ),
        ArtifactStatusRow(
            "Public intel",
            row_statuses.public_intel,
            public_intel_details(
                intel_path,
                context.intel_validation,
                context.intel_error,
                context.latest_run_id,
            ),
        ),
        ArtifactStatusRow(
            "Static site",
            row_statuses.static_site,
            static_site_details(
                site_dir / "index.html",
                context.static_site_health,
                context.latest_run_id,
            ),
        ),
        ArtifactStatusRow(
            "Site bundle",
            row_statuses.site_bundle,
            site_bundle_details(bundle_dir, context.site_bundle_health, context.latest_run_id),
        ),
    ]


__all__ = ["ArtifactStatusRow", "artifact_status_rows"]
