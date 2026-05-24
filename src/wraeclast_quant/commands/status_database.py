from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.status_database_rendering import console, print_database_health_result
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.health import DatabaseHealthError, check_database_health


def register(app: typer.Typer) -> None:
    @app.command("db-check")
    def db_check(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        try:
            result = check_database_health(database_path)
        except DatabaseHealthError as error:
            raise typer.BadParameter(str(error)) from error

        if result is None:
            console.print("No database found.")
            return

        print_database_health_result(result)
        console.print("Database check is read-only. No files were written.")
