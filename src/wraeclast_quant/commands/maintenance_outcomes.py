from __future__ import annotations

import typer
from wraeclast_quant.commands.maintenance_outcome_records import (
    register as register_record_commands,
)
from wraeclast_quant.commands.maintenance_outcome_reports import (
    register as register_report_commands,
)
from wraeclast_quant.commands.maintenance_outcome_review_queue import (
    register as register_review_queue_commands,
)


def register(app: typer.Typer) -> None:
    register_record_commands(app)
    register_review_queue_commands(app)
    register_report_commands(app)
