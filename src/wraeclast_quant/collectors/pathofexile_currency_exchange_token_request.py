from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_token_models import (
    TOKEN_ENDPOINT_URL,
    CurrencyExchangeTokenRequestPlan,
)


def currency_exchange_token_request_plan(
    *,
    scope: str,
    client_id: str,
    user_agent: str | None,
    ready: bool,
    blockers: tuple[str, ...],
) -> CurrencyExchangeTokenRequestPlan:
    return CurrencyExchangeTokenRequestPlan(
        token_url=TOKEN_ENDPOINT_URL,
        grant_type="client_credentials",
        scope=scope,
        client_id=client_id.strip(),
        user_agent=user_agent,
        form_fields=("client_id", "client_secret", "grant_type", "scope"),
        ready=ready,
        blockers=blockers,
    )


__all__ = ["currency_exchange_token_request_plan"]
