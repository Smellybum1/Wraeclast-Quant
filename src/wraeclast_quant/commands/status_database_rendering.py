from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.health import DatabaseHealthResult

console = Console(width=260)


def print_database_health_result(result: DatabaseHealthResult) -> None:
    table = Table(title="SQLite Database Check")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Database", str(result.database_path))
    table.add_row("Overall", "ok" if result.ok else "needs attention")
    table.add_row("Schema version", result.schema_version)
    table.add_row("Integrity", "ok" if result.integrity_ok else "failed")
    table.add_row("Integrity message", result.integrity_message)
    table.add_row("Required tables", "ok" if result.schema_ok else "missing")
    table.add_row("Required table names", ", ".join(result.required_tables))
    table.add_row("Missing tables", ", ".join(result.missing_tables))
    table.add_row("Size bytes", str(result.size_bytes))
    table.add_row("Analysis runs", _optional_int(result.analysis_run_count))
    table.add_row("Scored opportunities", _optional_int(result.scored_opportunity_count))
    table.add_row("Report artifacts", _optional_int(result.report_artifact_count))
    table.add_row("Recommendation outcomes", _optional_int(result.recommendation_outcome_count))
    table.add_row("Latest run", _optional_int(result.latest_run_id, none_value="none"))
    table.add_row("Latest source", result.latest_run_source_mode or "")
    table.add_row("Latest items", _optional_int(result.latest_run_item_count))
    table.add_row("Latest created", result.latest_run_created_at or "")
    console.print(table)


def _optional_int(value: int | None, none_value: str = "") -> str:
    return none_value if value is None else str(value)
