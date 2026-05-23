from __future__ import annotations

import typer

from wraeclast_quant.commands.connectors import register as register_connector_commands
from wraeclast_quant.commands.daily import register as register_daily_commands
from wraeclast_quant.commands.intake import register as register_intake_commands
from wraeclast_quant.commands.maintenance import register as register_maintenance_commands
from wraeclast_quant.commands.reports import register as register_report_commands
from wraeclast_quant.commands.resources import register as register_resource_commands
from wraeclast_quant.commands.snapshots import register as register_snapshot_commands
from wraeclast_quant.commands.status import register as register_status_commands

app = typer.Typer(help="Wraeclast Quant market intelligence CLI.")

register_status_commands(app)
register_snapshot_commands(app)
register_report_commands(app)
register_daily_commands(app)
register_maintenance_commands(app)
register_resource_commands(app)
register_connector_commands(app)
register_intake_commands(app)
