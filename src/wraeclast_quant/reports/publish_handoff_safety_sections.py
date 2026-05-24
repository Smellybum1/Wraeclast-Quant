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
    ]


__all__ = ["manual_checklist_lines", "safety_boundary_lines"]
