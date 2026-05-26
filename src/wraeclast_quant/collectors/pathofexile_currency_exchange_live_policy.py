from __future__ import annotations

OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS = (
    "Live connector collection is unsupported for Path of Exile Currency Exchange API.",
    "OAuth token exchange and refresh handling are not implemented.",
    "Credential storage outside the repo is not implemented.",
    "Dynamic response rate-limit parsing and cache writes are not implemented.",
    "Use raw fixture dry-runs and preview diagnostics until live runtime work is implemented.",
)


def official_currency_exchange_live_blockers() -> list[str]:
    return list(OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS)


__all__ = [
    "OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS",
    "official_currency_exchange_live_blockers",
]
