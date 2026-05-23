from __future__ import annotations

import typer

from wraeclast_quant.commands.connector_review_check import register as register_check_command
from wraeclast_quant.commands.connector_review_drafts import register as register_draft_commands
from wraeclast_quant.commands.connector_review_status import register as register_status_commands


def register(app: typer.Typer) -> None:
    register_draft_commands(app)
    register_status_commands(app)
    register_check_command(app)
