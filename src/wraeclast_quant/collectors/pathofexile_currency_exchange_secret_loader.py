from __future__ import annotations

from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_models import (
    CurrencyExchangeClientSecretResult,
    CurrencyExchangeSecretSource,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_sources import (
    secret_source_blockers,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_values import (
    load_currency_exchange_env_secret,
    load_currency_exchange_file_secret,
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
        return load_currency_exchange_env_secret(secret_source, env)
    if secret_source.kind == "file":
        return load_currency_exchange_file_secret(secret_source)
    return CurrencyExchangeClientSecretResult(
        ready=False,
        secret=None,
        source_description=None,
        blockers=("client secret source kind must be env or file.",),
    )


__all__ = ["load_currency_exchange_client_secret"]
