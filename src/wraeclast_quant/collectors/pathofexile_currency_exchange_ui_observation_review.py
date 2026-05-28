from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_formatting import (
    currency_name,
    markdown_cell,
    ratio_summary,
    stock_row_summary,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiObservation,
    CurrencyExchangeUiObservationSnapshot,
)


def currency_exchange_ui_observation_review_notes(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> str:
    lines = [
        "# Currency Exchange UI Observation Review Notes",
        "",
        "Local review notes only. This file is generated from manually transcribed in-game UI rows.",
        "No OAuth, live HTTP, scraping, OCR, game-client automation, snapshots, outcome recording, or publishing were performed.",
        "",
        f"- League: {snapshot.league}",
        f"- Observed at: {snapshot.observed_at or 'not supplied'}",
        f"- Observations: {len(snapshot.observations)}",
        "",
        "| Pair | Market ratio | Visible stock | Rows | Notes |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for observation in snapshot.observations:
        league = observation.league or snapshot.league
        pair = f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)"
        rows = "; ".join(stock_row_summary(row) for row in observation.stock_rows)
        if observation.no_stock and not rows:
            rows = "No stock"
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(pair),
                    markdown_cell(ratio_summary(observation.market_ratio, observation.no_stock)),
                    str(_visible_stock_total(observation)),
                    markdown_cell(rows or "none"),
                    markdown_cell(observation.notes or ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Capture Review Flags",
            "",
            *currency_exchange_ui_observation_review_flags(snapshot),
            "",
            "Use this sidecar while choosing local outcome labels after `wq daily --input-path <manual-import-output>`.",
            "Do not record outcomes until a human review decision has been made.",
            "",
        ]
    )
    return "\n".join(lines)


def currency_exchange_ui_observation_review_flags(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> list[str]:
    flags = currency_exchange_ui_observation_capture_review_flags(snapshot)
    if not flags:
        return ["- No capture review flags detected."]
    return flags


def currency_exchange_ui_observation_capture_review_flags(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> list[str]:
    flags: list[str] = []
    for observation in snapshot.observations:
        league = observation.league or snapshot.league
        pair = f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)"
        has_rows = bool(observation.stock_rows)
        if observation.no_stock:
            flags.append(
                f"- {pair}: No Stock was transcribed; verify this after the next market "
                "refresh before treating the absence as durable evidence."
            )
        elif not has_rows and observation.market_ratio is not None:
            flags.append(
                f"- {pair}: ratio-only capture; add visible stock-ladder rows before "
                "`wq daily` if possible because scoring treats missing stock conservatively."
            )
        elif not has_rows:
            flags.append(
                f"- {pair}: missing market ratio and stock-ladder rows; "
                "recapture before `wq daily` if possible."
            )
        elif observation.market_ratio is None:
            flags.append(
                f"- {pair}: stock-ladder rows were captured without an order-entry market "
                "ratio; verify the ratio before outcome review."
            )
    return flags


def _visible_stock_total(observation: CurrencyExchangeUiObservation) -> int:
    return sum(row.stock for row in observation.stock_rows)


__all__ = [
    "currency_exchange_ui_observation_capture_review_flags",
    "currency_exchange_ui_observation_review_flags",
    "currency_exchange_ui_observation_review_notes",
]
