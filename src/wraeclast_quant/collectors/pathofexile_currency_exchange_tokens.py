from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


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


def preview_currency_exchange_token_response(
    payload: Mapping[str, object],
    *,
    expected_scope: str = DEFAULT_SCOPE,
) -> CurrencyExchangeTokenResponsePreview:
    token_type = _optional_str(payload.get("token_type"))
    scope = _optional_str(payload.get("scope"))
    expires_in = _optional_int(payload.get("expires_in"))
    access_token_present = bool(_optional_str(payload.get("access_token")))
    blockers = _token_response_blockers(
        access_token_present=access_token_present,
        token_type=token_type,
        scope=scope,
        expected_scope=expected_scope,
    )
    return CurrencyExchangeTokenResponsePreview(
        ready=not blockers,
        token_type=token_type,
        scope=scope,
        expires_in=expires_in,
        access_token_present=access_token_present,
        blockers=tuple(blockers),
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


def _token_response_blockers(
    *,
    access_token_present: bool,
    token_type: str | None,
    scope: str | None,
    expected_scope: str,
) -> list[str]:
    blockers: list[str] = []
    if not access_token_present:
        blockers.append("access token is missing.")
    if (token_type or "").lower() != "bearer":
        blockers.append("token_type must be bearer.")
    if scope != expected_scope:
        blockers.append("token scope must be service:cxapi.")
    return blockers


def _optional_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _optional_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


__all__ = [
    "CurrencyExchangeTokenRequestPlan",
    "CurrencyExchangeTokenResponsePreview",
    "TOKEN_ENDPOINT_URL",
    "currency_exchange_token_request_plan",
    "preview_currency_exchange_token_response",
]
