from __future__ import annotations

import typer

from wraeclast_quant.commands.report_site import register as register_site_command
from wraeclast_quant.commands.report_site_bundle import register as register_site_bundle_command
from wraeclast_quant.commands.report_validate_intel import register as register_validate_intel_command


def register(app: typer.Typer) -> None:
    register_site_command(app)
    register_validate_intel_command(app)
    register_site_bundle_command(app)
