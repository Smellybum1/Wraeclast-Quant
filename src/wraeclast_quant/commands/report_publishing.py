from __future__ import annotations

import typer

from wraeclast_quant.commands.report_publish_check import register as register_publish_check_command
from wraeclast_quant.commands.report_publish_handoff import register as register_publish_handoff_command
from wraeclast_quant.commands.report_site_contract import register as register_site_contract_command


def register(app: typer.Typer) -> None:
    register_publish_check_command(app)
    register_publish_handoff_command(app)
    register_site_contract_command(app)
