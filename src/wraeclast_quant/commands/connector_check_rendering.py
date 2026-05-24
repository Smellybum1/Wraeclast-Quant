from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorCheckResult


def print_connector_check(result: ConnectorCheckResult) -> None:
    table = Table(title="Connector Review Check")
    for column in [
        "Resource",
        "Access Method",
        "Preflight",
        "Ready",
        "Cache TTL",
        "Rate Limit",
        "Blockers",
    ]:
        table.add_column(column, no_wrap=column != "Blockers")

    review = result.review
    preflight_status = result.preflight.status if result.preflight is not None else "missing"
    table.add_row(
        review.resource_name,
        review.access_method,
        preflight_status,
        "yes" if result.ready else "no",
        str(review.cache_ttl_seconds),
        f"{review.rate_limit_per_minute:g}/min",
        "\n".join(result.blockers) if result.blockers else "None",
    )
    console.print(table)
