from __future__ import annotations

import typer

from wraeclast_quant.commands.connector_review_evidence_command import register as register_evidence_command
from wraeclast_quant.commands.connector_review_status_command import register as register_status_command


def register(app: typer.Typer) -> None:
    register_evidence_command(app)
    register_status_command(app)
