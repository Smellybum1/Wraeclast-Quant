from __future__ import annotations

from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_models import (
    CurrencyExchangeClientSecret,
    CurrencyExchangeClientSecretResult,
    CurrencyExchangeSecretSource,
)


def load_currency_exchange_env_secret(
    secret_source: CurrencyExchangeSecretSource,
    env: Mapping[str, str],
) -> CurrencyExchangeClientSecretResult:
    value = env.get(secret_source.identifier, "").strip()
    if not value:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description=f"env:{secret_source.identifier}",
            blockers=("client secret environment variable is empty or missing.",),
        )
    return CurrencyExchangeClientSecretResult(
        ready=True,
        secret=CurrencyExchangeClientSecret(value=value, source=secret_source),
        source_description=f"env:{secret_source.identifier}",
        blockers=(),
    )


def load_currency_exchange_file_secret(
    secret_source: CurrencyExchangeSecretSource,
) -> CurrencyExchangeClientSecretResult:
    path = Path(secret_source.identifier).expanduser()
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description="file",
            blockers=("client secret file could not be read.",),
        )
    if not value:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description="file",
            blockers=("client secret file is empty.",),
        )
    return CurrencyExchangeClientSecretResult(
        ready=True,
        secret=CurrencyExchangeClientSecret(value=value, source=secret_source),
        source_description="file",
        blockers=(),
    )


__all__ = [
    "load_currency_exchange_env_secret",
    "load_currency_exchange_file_secret",
]
