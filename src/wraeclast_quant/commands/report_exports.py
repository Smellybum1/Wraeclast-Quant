from __future__ import annotations

import typer

from wraeclast_quant.commands.report_market_brief import register as register_market_brief_command
from wraeclast_quant.commands.report_public_intel_export import register as register_public_intel_export_command
from wraeclast_quant.commands.report_stash_ninja_watchlist import (
    register as register_stash_ninja_watchlist_command,
)


def register(app: typer.Typer) -> None:
    register_market_brief_command(app)
    register_public_intel_export_command(app)
    register_stash_ninja_watchlist_command(app)
