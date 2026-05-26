from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_secrets import (
    DEFAULT_CLIENT_SECRET_ENV,
    DEFAULT_CLIENT_SECRET_FILE_ENV,
    CurrencyExchangeClientSecret,
    CurrencyExchangeClientSecretResult,
    CurrencyExchangeSecretSource,
    load_currency_exchange_client_secret,
    redact_currency_exchange_secret_text,
    secret_source_blockers,
    secret_source_from_env,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_tokens import (
    CurrencyExchangeTokenRequestPlan,
    CurrencyExchangeTokenResponsePreview,
    currency_exchange_token_request_plan,
    preview_currency_exchange_token_response,
)
from wraeclast_quant.config.fetch_policy_models import FetchPlan


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


def currency_exchange_runtime_settings_from_env(
    env: Mapping[str, str],
    *,
    client_id: str = "",
    app_version: str = "",
    contact: str = "",
    realm: str = DEFAULT_REALM,
    request_budget: int = DEFAULT_REQUEST_BUDGET,
    client_secret_env: str = DEFAULT_CLIENT_SECRET_ENV,
    client_secret_file_env: str = DEFAULT_CLIENT_SECRET_FILE_ENV,
) -> CurrencyExchangeRuntimeSettings:
    return CurrencyExchangeRuntimeSettings(
        client_id=client_id,
        app_version=app_version,
        contact=contact,
        realm=realm,
        request_budget=request_budget,
        secret_source=secret_source_from_env(
            env,
            client_secret_env=client_secret_env,
            client_secret_file_env=client_secret_file_env,
        ),
    )


def preview_currency_exchange_runtime_preflight(
    settings: CurrencyExchangeRuntimeSettings,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeRuntimePreflight:
    blockers = _runtime_blockers(settings, Path(workspace_root))
    user_agent = None if blockers else currency_exchange_user_agent(settings)
    return CurrencyExchangeRuntimePreflight(
        ready=not blockers,
        user_agent=user_agent,
        blockers=tuple(blockers),
    )


def preview_currency_exchange_runtime_plan(
    settings: CurrencyExchangeRuntimeSettings,
    fetch_plan: FetchPlan,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeRuntimePlan:
    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=workspace_root,
    )
    return CurrencyExchangeRuntimePlan(
        resource_name=fetch_plan.resource_name,
        endpoint_path=f"/currency-exchange/{settings.realm}",
        realm=settings.realm,
        scope=settings.scope,
        token_grant_type="client_credentials",
        cache_path=fetch_plan.cache_path,
        request_budget=settings.request_budget,
        user_agent=preflight.user_agent,
        ready=preflight.ready,
        blockers=preflight.blockers,
    )


def currency_exchange_user_agent(settings: CurrencyExchangeRuntimeSettings) -> str:
    return (
        f"OAuth {settings.client_id.strip()}/{settings.app_version.strip()} "
        f"(contact: {settings.contact.strip()}) WraeclastQuant"
    )


def preview_currency_exchange_token_request_plan(
    settings: CurrencyExchangeRuntimeSettings,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeTokenRequestPlan:
    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=workspace_root,
    )
    return currency_exchange_token_request_plan(
        scope=settings.scope,
        client_id=settings.client_id.strip(),
        user_agent=preflight.user_agent,
        ready=preflight.ready,
        blockers=preflight.blockers,
    )


def _runtime_blockers(
    settings: CurrencyExchangeRuntimeSettings,
    workspace_root: Path,
) -> list[str]:
    blockers: list[str] = []
    if not settings.client_id.strip():
        blockers.append("client_id is required.")
    if not settings.app_version.strip():
        blockers.append("app_version is required.")
    if not settings.contact.strip():
        blockers.append("user-agent contact is required.")
    if settings.realm != DEFAULT_REALM:
        blockers.append("Currency Exchange runtime currently supports only the poe2 realm.")
    if settings.scope != DEFAULT_SCOPE:
        blockers.append("Currency Exchange runtime requires the service:cxapi scope.")
    if settings.request_budget < 1:
        blockers.append("request_budget must be at least 1.")
    blockers.extend(secret_source_blockers(settings.secret_source, workspace_root))
    return blockers


__all__ = [
    "CurrencyExchangeClientSecret",
    "CurrencyExchangeClientSecretResult",
    "CurrencyExchangeRuntimePreflight",
    "CurrencyExchangeRuntimePlan",
    "CurrencyExchangeRuntimeSettings",
    "CurrencyExchangeSecretSource",
    "CurrencyExchangeTokenRequestPlan",
    "CurrencyExchangeTokenResponsePreview",
    "currency_exchange_runtime_settings_from_env",
    "currency_exchange_user_agent",
    "load_currency_exchange_client_secret",
    "preview_currency_exchange_runtime_plan",
    "preview_currency_exchange_runtime_preflight",
    "preview_currency_exchange_token_request_plan",
    "preview_currency_exchange_token_response",
    "redact_currency_exchange_secret_text",
]
