from __future__ import annotations

from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime_models import (
    DEFAULT_REALM,
    DEFAULT_REQUEST_BUDGET,
    CurrencyExchangeRuntimePlan,
    CurrencyExchangeRuntimeSettings,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime_preflight import (
    currency_exchange_user_agent,
    preview_currency_exchange_runtime_preflight,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secrets import (
    DEFAULT_CLIENT_SECRET_ENV,
    DEFAULT_CLIENT_SECRET_FILE_ENV,
    secret_source_from_env,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_tokens import (
    CurrencyExchangeTokenRequestPlan,
    currency_exchange_token_request_plan,
)
from wraeclast_quant.config.fetch_policy_models import FetchPlan


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


__all__ = [
    "currency_exchange_runtime_settings_from_env",
    "currency_exchange_user_agent",
    "preview_currency_exchange_runtime_plan",
    "preview_currency_exchange_runtime_preflight",
    "preview_currency_exchange_token_request_plan",
]
