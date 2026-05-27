from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.commands.status_health_artifacts import (
    fresh_artifact_status,
    market_brief_status,
    public_intel_run_id,
    public_intel_status,
    site_bundle_run_id,
    site_bundle_status,
    static_site_run_id,
    static_site_status,
)
from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_stash_ninja_artifact import (
    stash_ninja_run_id,
    stash_ninja_status,
)


@dataclass(frozen=True)
class ArtifactRowStatuses:
    market_brief: str
    public_intel: str
    static_site: str
    site_bundle: str
    stash_ninja: str

    def strict_rows(self) -> list[tuple[str, str]]:
        return [
            ("Market brief", self.market_brief),
            ("Public intel", self.public_intel),
            ("Static site", self.static_site),
            ("Site bundle", self.site_bundle),
            ("Stash-Ninja handoff", self.stash_ninja),
        ]


def build_artifact_row_statuses(
    context: StatusHealthContext,
    *,
    intel_path: Path,
) -> ArtifactRowStatuses:
    return ArtifactRowStatuses(
        market_brief=market_brief_status(context.market_brief_health),
        public_intel=fresh_artifact_status(
            public_intel_status(intel_path, context.intel_validation, context.intel_error),
            public_intel_run_id(context.intel_validation),
            context.latest_run_id,
        ),
        static_site=fresh_artifact_status(
            static_site_status(context.static_site_health),
            static_site_run_id(context.static_site_health),
            context.latest_run_id,
        ),
        site_bundle=fresh_artifact_status(
            site_bundle_status(context.site_bundle_health),
            site_bundle_run_id(context.site_bundle_health),
            context.latest_run_id,
        ),
        stash_ninja=fresh_artifact_status(
            stash_ninja_status(context.stash_ninja_health),
            stash_ninja_run_id(context.stash_ninja_health),
            context.latest_run_id,
        ),
    )


__all__ = ["ArtifactRowStatuses", "build_artifact_row_statuses"]
