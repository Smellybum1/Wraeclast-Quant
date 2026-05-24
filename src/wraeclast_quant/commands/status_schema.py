from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.schema import (
    REQUIRED_SQLITE_TABLES,
    SQLITE_SCHEMA_VERSION,
    SQLITE_TABLE_DESCRIPTIONS,
)

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("schema")
    def schema() -> None:
        table = Table(title=f"SQLite Schema Contract v{SQLITE_SCHEMA_VERSION}")
        table.add_column("Table")
        table.add_column("Required", no_wrap=True)
        table.add_column("Description")
        for table_name in sorted(REQUIRED_SQLITE_TABLES):
            table.add_row(
                table_name,
                "yes",
                SQLITE_TABLE_DESCRIPTIONS.get(table_name, ""),
            )
        console.print(table)
        console.print("Schema inspection is read-only. No database was opened or written.")
