from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console(width=260)


def print_opportunities(title: str, opportunities) -> None:
    table = Table(title=title)
    table.add_column("Item")
    table.add_column("Score", justify="right")
    table.add_column("Action")
    for opportunity in opportunities:
        table.add_row(
            opportunity.item_name,
            f"{opportunity.opportunity_score:.2f}",
            opportunity.action,
        )
    console.print(table)
