from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import metadata_tags
from wraeclast_quant.reports.static_site_page_sections import dashboard_sections
from wraeclast_quant.reports.static_site_styles import static_site_css


def render_static_site(payload: dict[str, Any]) -> str:
    latest_run = payload.get("latest_run") or {}
    compliance = payload.get("compliance_summary") or {}
    status_counts = compliance.get("status_counts") or {}
    changes = payload.get("snapshot_changes") or {}

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            *metadata_tags(payload, latest_run),
            "  <title>Wraeclast Quant</title>",
            f"  <style>{static_site_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            "    <header>",
            "      <h1>Wraeclast Quant</h1>",
            "      <p>Local market intelligence preview. Research output only.</p>",
            "    </header>",
            *dashboard_sections(payload, latest_run, compliance, status_counts, changes),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )
