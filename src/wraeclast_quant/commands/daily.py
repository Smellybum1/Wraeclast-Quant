from __future__ import annotations

import typer

from wraeclast_quant.commands.daily_run import register as register_daily_run_command
from wraeclast_quant.commands.daily_schedule import register as register_schedule_helper_command


def register(app: typer.Typer) -> None:
    register_daily_run_command(app)
    register_schedule_helper_command(app)
