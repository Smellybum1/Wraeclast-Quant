from __future__ import annotations

from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime_models import (
    DEFAULT_REALM,
    DEFAULT_SCOPE,
    CurrencyExchangeRuntimePreflight,
    CurrencyExchangeRuntimeSettings,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secrets import (
    secret_source_blockers,
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


def currency_exchange_user_agent(settings: CurrencyExchangeRuntimeSettings) -> str:
    return (
        f"OAuth {settings.client_id.strip()}/{settings.app_version.strip()} "
        f"(contact: {settings.contact.strip()}) WraeclastQuant"
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
    "currency_exchange_user_agent",
    "preview_currency_exchange_runtime_preflight",
]
