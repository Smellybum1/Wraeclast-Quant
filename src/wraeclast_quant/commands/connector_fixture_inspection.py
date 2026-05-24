from __future__ import annotations

import typer

from wraeclast_quant.commands.connector_dry_run_command import register as register_dry_run_command
from wraeclast_quant.commands.connector_fixture_run_command import register as register_fixture_run_command


def register(app: typer.Typer) -> None:
    register_fixture_run_command(app)
    register_dry_run_command(app)
