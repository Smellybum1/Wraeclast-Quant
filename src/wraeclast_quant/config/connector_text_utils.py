from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from wraeclast_quant.config.connector_policy_models import (
    ConnectorApprovalHelperResult,
    ConnectorCheckResult,
)


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def safe_url(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    parts = urlsplit(normalized)
    if not parts.scheme or not parts.netloc:
        return single_line(normalized)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def report_row_value(check: str, value: str) -> str:
    if check in {"Source terms URL", "Robots/API policy URL"}:
        return safe_url(value)
    if check == "Review notes":
        return "recorded" if value.strip() else ""
    return value


def markdown_cell(value: str) -> str:
    return single_line(value).replace("|", "\\|")


def markdown_value(value: str) -> str:
    normalized = single_line(value)
    return normalized or "`None`"


def single_line(value: str) -> str:
    return " ".join(str(value).split())


def next_step(
    check: ConnectorCheckResult,
    approval: ConnectorApprovalHelperResult,
) -> str:
    if check.ready:
        return "Connector review is ready for `wq connector-plan` and source-specific implementation planning."
    if approval.suggestion_available:
        return f"After human approval, manually update `RESOURCES.md` with `{approval.approval_suggestion}`, then rerun `wq connector-check`."
    return "Resolve blockers before source approval or connector planning."
