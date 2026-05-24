from __future__ import annotations

from typing import Any

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
)
from wraeclast_quant.config.connector_policy_utils import (
    markdown_value,
    next_step,
    yes_no,
)


def blockers_section(check: ConnectorCheckResult) -> list[str]:
    lines = ["## Blockers", ""]
    if check.blockers:
        lines.extend(f"- {markdown_value(blocker)}" for blocker in check.blockers)
    else:
        lines.append("- None")
    return lines


def fetch_plan_section(fetch_plan: Any) -> list[str]:
    lines = ["", "## Fetch Plan Summary", ""]
    if fetch_plan is None:
        lines.append("- No fetch plan is available until connector-check passes.")
    else:
        lines.extend(
            [
                f"- Cache path: `{fetch_plan.cache_path}`",
                f"- Cache TTL: `{fetch_plan.cache_ttl_seconds}s`",
                f"- Rate limit: `{fetch_plan.rate_limit_per_minute:g}/min`",
                f"- Minimum request interval: `{fetch_plan.min_seconds_between_requests:.2f}s`",
                f"- Dry-run required: `{yes_no(fetch_plan.dry_run_required)}`",
                f"- Derived-only public export: `{yes_no(fetch_plan.public_export_derived_only)}`",
            ]
        )
    return lines


def next_step_section(
    check: ConnectorCheckResult,
    approval: ConnectorApprovalHelperResult,
) -> list[str]:
    return [
        "",
        "## Next Step",
        "",
        next_step(check, approval),
        "",
    ]


__all__ = ["blockers_section", "fetch_plan_section", "next_step_section"]
