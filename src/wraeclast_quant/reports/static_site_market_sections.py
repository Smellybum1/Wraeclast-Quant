from __future__ import annotations

from wraeclast_quant.reports.static_site_alert_sections import alerts_section
from wraeclast_quant.reports.static_site_opportunity_sections import opportunities_section
from wraeclast_quant.reports.static_site_snapshot_sections import (
    movers_section,
    status_changes_section,
)


__all__ = [
    "alerts_section",
    "movers_section",
    "opportunities_section",
    "status_changes_section",
]
