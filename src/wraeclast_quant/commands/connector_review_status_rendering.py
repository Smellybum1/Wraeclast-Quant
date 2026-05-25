from __future__ import annotations

from rich.markup import escape
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorReviewStatus


def print_connector_review_status(status: ConnectorReviewStatus) -> None:
    table = Table(title="Connector Review Status")
    for column in ["Check", "Value", "Status"]:
        table.add_column(column, no_wrap=column != "Value")

    for row in status.rows:
        table.add_row(escape(row.check), escape(row.value), escape(row.status))

    blockers = status.check_result.blockers
    blockers_text = "\n".join(blockers) if blockers else "None"
    table.add_row("Blockers", escape(blockers_text), "blocked" if blockers else "ok")
    console.print(table)
