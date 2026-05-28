from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console, print_opportunities
from wraeclast_quant.importers.manual import SIGNAL_FIELDS
from wraeclast_quant.importers.summary import ManualImportSummary
from wraeclast_quant.intelligence.scoring import ScoredOpportunity


def manual_import_daily_next_action(input_path: object) -> str:
    return f"Next: wq daily --input-path {input_path}"


def manual_import_validate_next_action(input_path: object) -> str:
    return f"Next: wq validate-import --input-path {input_path}"


def print_manual_import_diagnostics(
    summary: ManualImportSummary,
    opportunities: list[ScoredOpportunity],
    limit: int,
) -> None:
    overview = Table(title="Manual Import Diagnostics")
    overview.add_column("Metric")
    overview.add_column("Value", justify="right")
    overview.add_row("Items", str(summary.item_count))
    overview.add_row("Average score", f"{summary.average_score:.2f}")
    overview.add_row("Minimum score", f"{summary.min_score:.2f}")
    overview.add_row("Maximum score", f"{summary.max_score:.2f}")
    for action, count in summary.action_counts.items():
        overview.add_row(f"{action} count", str(count))
    console.print(overview)

    signals = Table(title="Signal Averages")
    signals.add_column("Signal")
    signals.add_column("Average", justify="right")
    for field in SIGNAL_FIELDS:
        signals.add_row(field, f"{summary.signal_averages[field]:.2f}")
    console.print(signals)

    print_opportunities("Top Imported Opportunities", opportunities[:limit])


__all__ = [
    "manual_import_daily_next_action",
    "manual_import_validate_next_action",
    "print_manual_import_diagnostics",
]
