from __future__ import annotations

from pathlib import Path

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorReviewReportResult


def print_connector_review_report_summary(report: ConnectorReviewReportResult, written_path: Path) -> None:
    table = Table(title="Connector Review Report")
    table.add_column("Field")
    table.add_column("Value", no_wrap=False)
    table.add_row("Resource", report.review.resource_name)
    table.add_row("Output path", str(written_path))
    table.add_row("Connector check", "ready" if report.check_result.ready else "not ready")
    table.add_row(
        "Approval suggestion",
        report.approval.approval_suggestion if report.approval.suggestion_available else "None",
    )
    table.add_row(
        "Blockers",
        "\n".join(report.check_result.blockers) if report.check_result.blockers else "None",
    )
    console.print(table)
    console.print("Connector review report is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector.")
