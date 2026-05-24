from __future__ import annotations

import typer

from wraeclast_quant.commands.status_database import register as register_database_command
from wraeclast_quant.commands.status_report import register as register_status_command
from wraeclast_quant.commands.status_schema import register as register_schema_command


def register(app: typer.Typer) -> None:
    register_schema_command(app)
    register_status_command(app)
    register_database_command(app)
