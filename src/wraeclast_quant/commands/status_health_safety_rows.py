from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row
from wraeclast_quant.commands.status_health_storage import backup_status, backup_status_details


def add_backup_and_safety_rows(
    status_rows: list[dict[str, str]],
    strict_rows: list[tuple[str, str]],
    context: StatusHealthContext,
) -> None:
    backup_row_status = backup_status(context.backups)
    strict_rows.append(("Backups", backup_row_status))
    add_status_row(status_rows, "Backups", backup_row_status, backup_status_details(context.backups))
    add_status_row(
        status_rows,
        "Safety boundary",
        "ok",
        "Local-only status check; collectors remain dry-run placeholders.",
    )
