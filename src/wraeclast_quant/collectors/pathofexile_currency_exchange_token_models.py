from __future__ import annotations

from dataclasses import dataclass


DEFAULT_SCOPE = "service:cxapi"
TOKEN_ENDPOINT_URL = "https://www.pathofexile.com/oauth/token"


@dataclass(frozen=True)
class CurrencyExchangeTokenResponsePreview:
    ready: bool
    token_type: str | None
    scope: str | None
    expires_in: int | None
    access_token_present: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CurrencyExchangeTokenRequestPlan:
    token_url: str
    grant_type: str
    scope: str
    client_id: str
    user_agent: str | None
    form_fields: tuple[str, ...]
    ready: bool
    blockers: tuple[str, ...]


__all__ = [
    "CurrencyExchangeTokenRequestPlan",
    "CurrencyExchangeTokenResponsePreview",
    "DEFAULT_SCOPE",
    "TOKEN_ENDPOINT_URL",
]
