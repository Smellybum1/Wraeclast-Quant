from __future__ import annotations

from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime_models import (
    DEFAULT_REALM,
    DEFAULT_REQUEST_BUDGET,
    CurrencyExchangeRuntimeSettings,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secrets import (
    DEFAULT_CLIENT_SECRET_ENV,
    DEFAULT_CLIENT_SECRET_FILE_ENV,
    secret_source_from_env,
)


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


__all__ = ["currency_exchange_runtime_settings_from_env"]
