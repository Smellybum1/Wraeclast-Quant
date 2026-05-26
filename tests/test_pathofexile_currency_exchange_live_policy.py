from wraeclast_quant.collectors.pathofexile_currency_exchange_live_policy import (
    OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS,
    official_currency_exchange_live_blockers,
)


def test_official_currency_exchange_live_blockers_are_failure_closed_copy() -> None:
    blockers = official_currency_exchange_live_blockers()
    blockers.append("mutated")

    assert "mutated" not in official_currency_exchange_live_blockers()
    assert blockers[:-1] == list(OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS)
    assert any("OAuth token exchange" in blocker for blocker in OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS)
    assert any("cache writes" in blocker for blocker in OFFICIAL_CURRENCY_EXCHANGE_LIVE_BLOCKERS)
