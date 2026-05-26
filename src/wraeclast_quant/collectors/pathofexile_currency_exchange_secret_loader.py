from __future__ import annotations

from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_models import (
    CurrencyExchangeClientSecret,
    CurrencyExchangeClientSecretResult,
    CurrencyExchangeSecretSource,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_sources import (
    secret_source_blockers,
)


def load_currency_exchange_client_secret(
    secret_source: CurrencyExchangeSecretSource | None,
    *,
    env: Mapping[str, str],
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeClientSecretResult:
    blockers = secret_source_blockers(secret_source, Path(workspace_root))
    if blockers:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description=None,
            blockers=tuple(blockers),
        )
    assert secret_source is not None
    if secret_source.kind == "env":
        return _load_env_secret(secret_source, env)
    if secret_source.kind == "file":
        return _load_file_secret(secret_source)
    return CurrencyExchangeClientSecretResult(
        ready=False,
        secret=None,
        source_description=None,
        blockers=("client secret source kind must be env or file.",),
    )


def _load_env_secret(
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


def _load_file_secret(
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


__all__ = ["load_currency_exchange_client_secret"]
