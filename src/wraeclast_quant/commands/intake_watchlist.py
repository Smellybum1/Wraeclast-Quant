from __future__ import annotations

import typer
from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.watchlist import top_watchlist
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS


def register(app: typer.Typer) -> None:
    @app.command()
    def watchlist() -> None:
        opportunities = top_watchlist(rank_opportunities(SAMPLE_ITEMS))
        table = Table(title="Watchlist")
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
