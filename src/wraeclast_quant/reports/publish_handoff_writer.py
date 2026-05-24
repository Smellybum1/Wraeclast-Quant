from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.publish_handoff_rendering import render_publish_handoff
from wraeclast_quant.reports.publish_models import PublishCheckResult

DEFAULT_PUBLISH_HANDOFF_PATH = Path("data/processed/publish_handoff.md")


def write_publish_handoff(
    result: PublishCheckResult,
    output_path: str | Path = DEFAULT_PUBLISH_HANDOFF_PATH,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_publish_handoff(result), encoding="utf-8")
    return path
