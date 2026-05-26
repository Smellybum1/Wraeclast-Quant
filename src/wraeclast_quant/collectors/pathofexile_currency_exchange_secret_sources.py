from __future__ import annotations

from pathlib import Path
from typing import Mapping

from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_models import (
    CurrencyExchangeSecretSource,
)


DEFAULT_CLIENT_SECRET_ENV = "WQ_POE_CLIENT_SECRET"
DEFAULT_CLIENT_SECRET_FILE_ENV = "WQ_POE_CLIENT_SECRET_FILE"


def secret_source_from_env(
    env: Mapping[str, str],
    *,
    client_secret_env: str,
    client_secret_file_env: str,
) -> CurrencyExchangeSecretSource | None:
    secret_file = env.get(client_secret_file_env, "").strip()
    if secret_file:
        return CurrencyExchangeSecretSource("file", secret_file)
    if env.get(client_secret_env, "").strip():
        return CurrencyExchangeSecretSource("env", client_secret_env)
    return None


def secret_source_blockers(
    secret_source: CurrencyExchangeSecretSource | None,
    workspace_root: Path,
) -> list[str]:
    if secret_source is None:
        return ["client secret source is required."]
    if secret_source.kind == "env":
        if not secret_source.identifier.strip():
            return ["client secret environment variable name is required."]
        return []
    if secret_source.kind == "file":
        if not secret_source.identifier.strip():
            return ["client secret file path is required."]
        if _path_is_inside_workspace(Path(secret_source.identifier), workspace_root):
            return ["client secret file must be outside the repository workspace."]
        return []
    return ["client secret source kind must be env or file."]


def _path_is_inside_workspace(path: Path, workspace_root: Path) -> bool:
    resolved_path = path.expanduser().resolve(strict=False)
    resolved_root = workspace_root.expanduser().resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return False
    return True


__all__ = [
    "DEFAULT_CLIENT_SECRET_ENV",
    "DEFAULT_CLIENT_SECRET_FILE_ENV",
    "secret_source_blockers",
    "secret_source_from_env",
]
