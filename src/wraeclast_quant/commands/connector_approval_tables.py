from __future__ import annotations

from pathlib import Path

from rich.table import Table

from wraeclast_quant.config.connector_policy import ConnectorApprovalHelperResult, ConnectorApprovalPatchResult


def connector_approval_helper_table(result: ConnectorApprovalHelperResult) -> Table:
    table = Table(title="Connector Approval Helper")
    for column in [
        "Resource",
        "ID",
        "Current Allowed Use",
        "Access",
        "Preflight",
        "Evidence Ready",
        "Connector Check",
        "Manual Approval Suggestion",
        "Reason / Blockers",
    ]:
        table.add_column(
            column,
            no_wrap=column not in {"Manual Approval Suggestion", "Reason / Blockers"},
        )

    resource = result.resource
    preflight_status = result.preflight.status if result.preflight is not None else "missing"
    blockers = "\n".join(result.blockers) if result.blockers else result.reason
    table.add_row(
        resource.name if resource is not None else result.review.resource_name,
        resource.id if resource is not None else "",
        resource.allowed_use if resource is not None else "",
        result.review.access_method,
        preflight_status,
        "yes" if result.evidence_ready else "no",
        "yes" if result.connector_check_ready else "no",
        result.approval_suggestion if result.suggestion_available else "None",
        blockers if result.blockers else result.reason,
    )
    return table


def connector_approval_patch_table(
    result: ConnectorApprovalPatchResult,
    written_path: Path | None,
) -> Table:
    table = Table(title="Connector Approval Patch Preview")
    table.add_column("Field")
    table.add_column("Value", no_wrap=False)
    table.add_row("Resource", result.review.resource_name)
    table.add_row("Patch available", "yes" if result.patch_available else "no")
    table.add_row("Output path", str(written_path) if written_path is not None else "None")
    table.add_row("Reason", result.reason)
    table.add_row("Blockers", "\n".join(result.blockers) if result.blockers else "None")
    return table


__all__ = ["connector_approval_helper_table", "connector_approval_patch_table"]
