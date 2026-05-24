from __future__ import annotations

from pathlib import Path

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorApprovalHelperResult, ConnectorApprovalPatchResult


def print_connector_approval_helper(result: ConnectorApprovalHelperResult) -> None:
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
    console.print(table)

    if result.suggestion_available:
        console.print("Manual approval suggestion:")
        console.print(result.approval_suggestion)
        console.print("This command is read-only. Manually edit RESOURCES.md only after approval.")
    else:
        console.print(result.reason)


def print_connector_approval_patch(result: ConnectorApprovalPatchResult, written_path: Path | None) -> None:
    table = Table(title="Connector Approval Patch Preview")
    table.add_column("Field")
    table.add_column("Value", no_wrap=False)
    table.add_row("Resource", result.review.resource_name)
    table.add_row("Patch available", "yes" if result.patch_available else "no")
    table.add_row("Output path", str(written_path) if written_path is not None else "None")
    table.add_row("Reason", result.reason)
    table.add_row("Blockers", "\n".join(result.blockers) if result.blockers else "None")
    console.print(table)
    console.print("Approval patch is advisory only. It did not edit RESOURCES.md, fetch data, or approve a connector.")
