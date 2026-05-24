from __future__ import annotations

import re
from pathlib import Path

import typer

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items


def validate_schedule_input(sample_data: bool, input_path: Path | None) -> None:
    if sample_data and input_path is not None:
        raise typer.BadParameter("Use either --sample-data or --input-path, not both.")
    if not sample_data and input_path is None:
        raise typer.BadParameter("Use --sample-data or --input-path for schedule helper.")
    if input_path is not None:
        try:
            load_manual_items(input_path)
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error


def validate_schedule_time(run_time: str) -> None:
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", run_time):
        raise typer.BadParameter("Use --time in HH:MM 24-hour format.")
