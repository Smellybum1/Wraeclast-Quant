from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.reports.site_bundle import ARCHIVE_NAME


@dataclass(frozen=True)
class PublishReadinessPaths:
    bundle_dir: Path
    archive_path: Path
    intel_path: Path
    index_path: Path


def publish_readiness_paths(bundle_dir: Path) -> PublishReadinessPaths:
    return PublishReadinessPaths(
        bundle_dir=bundle_dir,
        archive_path=bundle_dir / ARCHIVE_NAME,
        intel_path=bundle_dir / "public_intel.json",
        index_path=bundle_dir / "index.html",
    )


__all__ = ["PublishReadinessPaths", "publish_readiness_paths"]
