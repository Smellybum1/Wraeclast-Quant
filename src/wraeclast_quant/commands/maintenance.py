from __future__ import annotations

import typer

from wraeclast_quant.commands.maintenance_backups import register as register_backup_commands
from wraeclast_quant.commands.maintenance_calibration import (
    register as register_calibration_commands,
)
from wraeclast_quant.commands.maintenance_migrations import (
    register as register_migration_commands,
)
from wraeclast_quant.commands.maintenance_outcomes import register as register_outcome_commands


def register(app: typer.Typer) -> None:
    register_backup_commands(app)
    register_migration_commands(app)
    register_outcome_commands(app)
    register_calibration_commands(app)
