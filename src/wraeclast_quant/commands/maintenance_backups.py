from __future__ import annotations

import typer

from wraeclast_quant.commands.maintenance_backup_create import (
    register as register_backup_create_commands,
)
from wraeclast_quant.commands.maintenance_backup_inspect import (
    register as register_backup_inspect_commands,
)
from wraeclast_quant.commands.maintenance_backup_restore import (
    register as register_backup_restore_commands,
)


def register(app: typer.Typer) -> None:
    register_backup_create_commands(app)
    register_backup_inspect_commands(app)
    register_backup_restore_commands(app)
