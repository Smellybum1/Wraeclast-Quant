from __future__ import annotations

from pathlib import Path
from typing import Any

from wraeclast_quant.reports.site_contract_summaries import (
    bundle_summary,
    public_intel_summary,
    static_site_summary,
)


def site_contract_artifact_summaries(bundle_dir: Path) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    public_intel = public_intel_summary(bundle_dir / "public_intel.json")
    static_site = static_site_summary(bundle_dir / "index.html")
    bundle = bundle_summary(bundle_dir)
    return public_intel, static_site, bundle


__all__ = ["site_contract_artifact_summaries"]
