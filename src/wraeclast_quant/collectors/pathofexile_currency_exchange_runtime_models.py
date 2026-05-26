from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_secrets import (
    CurrencyExchangeSecretSource,
)


DEFAULT_REALM = "poe2"
DEFAULT_SCOPE = "service:cxapi"
DEFAULT_REQUEST_BUDGET = 1


@dataclass(frozen=True)
class CurrencyExchangeRuntimeSettings:
    client_id: str
    app_version: str
    contact: str
    secret_source: CurrencyExchangeSecretSource | None = None
    realm: str = DEFAULT_REALM
    scope: str = DEFAULT_SCOPE
    request_budget: int = DEFAULT_REQUEST_BUDGET


@dataclass(frozen=True)
class CurrencyExchangeRuntimePreflight:
    ready: bool
    user_agent: str | None
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CurrencyExchangeRuntimePlan:
    resource_name: str
    endpoint_path: str
    realm: str
    scope: str
    token_grant_type: str
    cache_path: Path
    request_budget: int
    user_agent: str | None
    ready: bool
    blockers: tuple[str, ...]


__all__ = [
    "DEFAULT_REALM",
    "DEFAULT_REQUEST_BUDGET",
    "DEFAULT_SCOPE",
    "CurrencyExchangeRuntimePlan",
    "CurrencyExchangeRuntimePreflight",
    "CurrencyExchangeRuntimeSettings",
]
