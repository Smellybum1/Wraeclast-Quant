from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row
from wraeclast_quant.commands.status_health_storage import (
    database_health_details,
    database_health_status,
    exists_label,
)


def add_overview_rows(
    status_rows: list[dict[str, str]],
    strict_rows: list[tuple[str, str]],
    context: StatusHealthContext,
    *,
    database_path: Path,
) -> None:
    add_status_row(
        status_rows,
        "Resources",
        "ok",
        f"{len(context.resources)} configured; {context.eligible_count} automation-eligible",
    )
    add_status_row(status_rows, "Database", exists_label(context.database_exists), str(database_path))

    database_health_row_status = database_health_status(context.database_health)
    strict_rows.append(("Database health", database_health_row_status))
    add_status_row(
        status_rows,
        "Database health",
        database_health_row_status,
        database_health_details(context.database_health),
    )


__all__ = ["add_overview_rows"]
