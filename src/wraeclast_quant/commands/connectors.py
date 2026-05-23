from __future__ import annotations

import typer

from wraeclast_quant.commands import (
    connector_approvals,
    connector_candidates_commands,
    connector_fixtures,
    connector_planning,
    connector_review_reports,
    connector_reviews,
)


def register(app: typer.Typer) -> None:
    connector_candidates_commands.register(app)
    connector_reviews.register(app)
    connector_approvals.register_helper(app)
    connector_review_reports.register(app)
    connector_approvals.register_patch(app)
    connector_fixtures.register(app)
    connector_planning.register(app)
