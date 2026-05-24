from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.config.compliance import ComplianceAssessment

console = Console(width=260)


def print_compliance_assessments(assessments: list[ComplianceAssessment]) -> None:
    table = Table(title="Resource Compliance")
    for column in [
        "Source",
        "Type",
        "Allowed Use",
        "Collector",
        "Status",
        "Automation",
        "Reason",
    ]:
        table.add_column(column, no_wrap=column != "Reason")

    for assessment in assessments:
        resource = assessment.resource
        table.add_row(
            resource.name,
            resource.type,
            resource.allowed_use,
            resource.collector or "placeholder",
            assessment.status,
            "yes" if assessment.automation_eligible else "no",
            assessment.reason,
        )
    console.print(table)
