from __future__ import annotations

import typer

from wraeclast_quant.commands.daily_schedule_command import register as register_schedule_helper_command


def register(app: typer.Typer) -> None:
    register_schedule_helper_command(app)
