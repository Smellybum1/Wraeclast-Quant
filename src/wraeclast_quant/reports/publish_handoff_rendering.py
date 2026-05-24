from __future__ import annotations

from datetime import UTC, datetime

from wraeclast_quant.reports.publish_handoff_sections import (
    blocker_lines,
    bundle_file_lines,
    manual_checklist_lines,
    readiness_check_lines,
    safety_boundary_lines,
    summary_lines,
)
from wraeclast_quant.reports.publish_models import PublishCheckResult


def render_publish_handoff(result: PublishCheckResult) -> str:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    lines = summary_lines(result, generated_at)
    lines.extend(bundle_file_lines(result.files))
    lines.extend(readiness_check_lines(result))
    lines.extend(blocker_lines(result.blockers))
    lines.extend(manual_checklist_lines())
    lines.extend(safety_boundary_lines())
    return "\n".join(lines)
