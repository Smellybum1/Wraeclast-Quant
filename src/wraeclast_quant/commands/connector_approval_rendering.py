from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_approval_tables import (
    connector_approval_helper_table,
    connector_approval_patch_table,
)
from wraeclast_quant.config.connector_policy import ConnectorApprovalHelperResult, ConnectorApprovalPatchResult


def print_connector_approval_helper(result: ConnectorApprovalHelperResult) -> None:
    console.print(connector_approval_helper_table(result))

    if result.suggestion_available:
        console.print("Manual approval suggestion:")
        console.print(result.approval_suggestion)
        console.print("This command is read-only. Manually edit RESOURCES.md only after approval.")
    else:
        console.print(result.reason)


def print_connector_approval_patch(result: ConnectorApprovalPatchResult, written_path: Path | None) -> None:
    console.print(connector_approval_patch_table(result, written_path))
    console.print("Approval patch is advisory only. It did not edit RESOURCES.md, fetch data, or approve a connector.")


__all__ = ["print_connector_approval_helper", "print_connector_approval_patch"]
