from __future__ import annotations

import typer

from wraeclast_quant.commands.intake_analysis import register as register_analysis_commands
from wraeclast_quant.commands.intake_manual_import import register as register_manual_import_commands
from wraeclast_quant.commands.intake_watchlist import register as register_watchlist_command


def register(app: typer.Typer) -> None:
    register_analysis_commands(app)
    register_manual_import_commands(app)
    register_watchlist_command(app)
