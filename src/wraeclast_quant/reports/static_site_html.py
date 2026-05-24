from __future__ import annotations

from wraeclast_quant.reports.static_site_formatting import (
    format_delta,
    format_score,
    format_trend_points,
)
from wraeclast_quant.reports.static_site_metadata import metadata_tags
from wraeclast_quant.reports.static_site_tables import (
    badge,
    is_html_cell,
    key_value_table,
    section,
    table,
)


__all__ = [
    "badge",
    "format_delta",
    "format_score",
    "format_trend_points",
    "is_html_cell",
    "key_value_table",
    "metadata_tags",
    "section",
    "table",
]
