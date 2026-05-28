from __future__ import annotations


def manual_checklist_lines() -> list[str]:
    return [
        "",
        "## Manual Publishing Checklist",
        "",
        "- [ ] Confirm `wq publish-check` reports ready.",
        "- [ ] Inspect the static dashboard locally.",
        "- [ ] Inspect `public_intel.json` for derived-only content.",
        "- [ ] Confirm the bundle archive contains only the expected static files.",
        "- [ ] Keep local review worksheets, outcome-decision files, and feedback reports out of the public handoff: `review_queue*.md`, `outcome_decisions*.json`, `outcome_review.md`, `calibration_report.md`, and `exile_ui_stash_ninja_watchlist.*`.",
        "- [ ] Manually publish outside Wraeclast Quant only if you choose to.",
        "",
    ]


def safety_boundary_lines() -> list[str]:
    return [
        "## Safety Boundary",
        "",
        "This handoff is local-only and derived-only. Wraeclast Quant did not upload, host, publish, start a server, make network calls, call webhooks, post to Discord, scrape sources, approve sources, automate gameplay, perform trades, send whispers, click UI, move characters, or interact with the game client.",
        "",
        "Do not include unprocessed signal payloads, source data excerpts, resource notes, credentials, cookies, tokens, or secret environment values in a public handoff.",
        "",
        "Local review worksheets, outcome-decision files, Stash-Ninja companion exports, outcome reports, and calibration reports are manual feedback-loop artifacts, not public handoff inputs.",
        "",
    ]


__all__ = ["manual_checklist_lines", "safety_boundary_lines"]
