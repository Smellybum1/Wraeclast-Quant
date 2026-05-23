from __future__ import annotations

import typer

from wraeclast_quant.commands import snapshot_alerts, snapshot_compare, snapshot_listing
from wraeclast_quant.commands.snapshot_compare import latest_comparison
from wraeclast_quant.commands.snapshot_rendering import print_alert_candidates, print_comparison


def register(app: typer.Typer) -> None:
    snapshot_listing.register(app)
    snapshot_compare.register(app)
    snapshot_alerts.register(app)
