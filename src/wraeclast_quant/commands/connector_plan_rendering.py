from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorReview
from wraeclast_quant.config.fetch_policy import FetchPlanResult


def print_connector_plan(review: ConnectorReview, result: FetchPlanResult) -> None:
    table = Table(title="Safe Fetch Plan")
    for column in [
        "Resource",
        "URL",
        "Access",
        "Cache Path",
        "TTL",
        "Rate Limit",
        "Min Interval",
        "Ready",
        "Blockers",
    ]:
        table.add_column(column, no_wrap=column not in {"URL", "Cache Path", "Blockers"})

    if result.plan is None:
        table.add_row(
            review.resource_name,
            "",
            review.access_method,
            "",
            str(review.cache_ttl_seconds),
            f"{review.rate_limit_per_minute:g}/min",
            "",
            "no",
            "\n".join(result.check.blockers),
        )
        console.print(table)
        return

    plan = result.plan
    table.add_row(
        plan.resource_name,
        plan.url,
        plan.access_method,
        str(plan.cache_path),
        str(plan.cache_ttl_seconds),
        f"{plan.rate_limit_per_minute:g}/min",
        f"{plan.min_seconds_between_requests:.2f}s",
        "yes",
        "None",
    )
    console.print(table)
    console.print("Fetch plan is local-only. No network requests were made and no files were written.")
